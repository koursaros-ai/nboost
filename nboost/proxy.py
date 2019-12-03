"""NBoost Proxy Class"""

from contextlib import suppress
from typing import Type, List
import socket
import json
import re
from httptools import HttpParserError
from nboost.types import Request, Response, URL
from nboost.protocol import HttpProtocol
from nboost.stats import ClassStatistics
from nboost.codex.base import BaseCodex
from nboost.model.base import BaseModel
from nboost.server import SocketServer
from nboost.logger import set_logger
from nboost.types import Choice
from nboost import PKG_PATH
from nboost.exceptions import (
    UpstreamConnectionError,
    UnknownRequest,
    FrontendRequest,
    MissingQuery
)


class HttpParserContext:
    """Context that reraises the __context__ of an HttpParserError"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, HttpParserError):
            raise exc_val.__context__


class Proxy(SocketServer):
    """The proxy object is the core of NBoost.
    The following __init__ contains the main executed functions in nboost.

    :param host: virtual host of the server.
    :param port: server port.
    :param uhost: host of the external search api.
    :param uport: search api port.
    :param multiplier: the factor to multiply the search request by. For
        example, in the case of Elasticsearch if the client requests 10
        results and the multiplier is 6, then the model should receive 60
        results to rank and refine down to 10 (better) results.
    :param field: a tag for the field in the search api result that the
        model should rank results by.
    :param model: uninitialized model class
    :param codex: uninitialized codex class
    """

    # statistical contexts
    STATIC_PATH = PKG_PATH.joinpath('resources/frontend')
    stats = ClassStatistics()

    def __init__(self, model: Type[BaseModel], codex: Type[BaseCodex],
                 uhost: str = '0.0.0.0', uport: int = 9200,
                 bufsize: int = 2048, verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs
        self.uaddress = (uhost, uport)
        self.bufsize = bufsize
        self.logger = set_logger(model.__name__, verbose=verbose)

        # pass command line arguments to instantiate each component
        self.model = model(verbose=verbose, **kwargs)
        self.codex = codex(verbose=verbose, **kwargs)

    def on_client_request_url(self, url: URL):
        """Method for screening the url path from the client request"""
        if url.path.startswith('/nboost'):
            raise FrontendRequest

        if not re.match(self.codex.SEARCH_PATH, url.path):
            raise UnknownRequest

    def set_protocol(self, sock: socket.socket) -> HttpProtocol:
        """Construct the protocol with the proxy settings"""
        protocol = HttpProtocol(sock)
        protocol.set_bufsize = self.bufsize
        return protocol

    @stats.time_context
    def proxy_send(self, client_socket, server_socket, buffer: bytearray):
        """Send buffered request to server and receive the rest of the original
        client request"""
        protocol = self.set_protocol(client_socket)
        protocol.set_request_parser()
        server_socket.send(buffer)
        protocol.feed(buffer)
        protocol.add_data_hook(server_socket.send)
        protocol.recv()

    @stats.time_context
    def proxy_recv(self, client_socket, server_socket):
        """Receive the proxied response and pipe to the client"""
        protocol = self.set_protocol(server_socket)
        protocol.set_response_parser()
        protocol.add_data_hook(client_socket.send)
        protocol.recv()

    @stats.time_context
    def client_recv(self, client_socket, request: Request, buffer: bytearray):
        """Receive client request and pipe to buffer in case of exceptions"""
        protocol = self.set_protocol(client_socket)
        protocol.set_request_parser()
        protocol.set_request(request)
        protocol.add_data_hook(buffer.extend)
        protocol.add_url_hook(self.on_client_request_url)
        protocol.recv()

    @staticmethod
    @stats.time_context
    def server_send(server_socket, request: Request):
        """Send magnified request to the server"""
        server_socket.send(request.prepare())

    @stats.time_context
    def server_recv(self, server_socket, response: Response):
        """Receive magnified request from the server"""
        protocol = self.set_protocol(server_socket)
        protocol.set_response_parser()
        protocol.set_response(response)
        protocol.recv()

    @staticmethod
    @stats.time_context
    def client_send(request: Request, response: Response, client_socket):
        """Send the ranked results to the client"""
        raw_response = response.prepare(request)
        client_socket.send(raw_response)

    @stats.time_context
    def model_rank(self, query: bytes, choices: List[Choice]) -> List[int]:
        """Rank the query and choices and return the argsorted indices"""
        return self.model.rank(query, choices)

    @stats.vars_context
    def record_topk_and_choices(self, topk: int = None, choices: list = None):
        """Add topk and choices to the running statistical averages"""

    @stats.vars_context
    def record_mrrs(self, upstream_mrr: float = None, model_mrr: float = None):
        """Add the upstream mrr and model mrr to the stats"""
        with suppress(ZeroDivisionError):
            self.record_search_boost(search_boost=model_mrr / upstream_mrr)

    @stats.vars_context
    def record_search_boost(self, search_boost: float = None):
        """Record the quotient of model mrr and upstream mrr"""

    @stats.time_context
    def server_connect(self, server_socket: socket.socket) -> None:
        """Connect proxied server socket"""
        try:
            server_socket.connect(self.uaddress)
        except ConnectionRefusedError:
            raise UpstreamConnectionError(*self.uaddress)

    @property
    def status(self) -> dict:
        """Return status dictionary in the case of a status request"""
        return {'multiplier': self.codex.multiplier, **self.stats.record,
                'description': 'NBoost, for search ranking.'}

    def calculate_mrrs(self, correct_cids: List[str], choices: List[Choice],
                       ranks: List[int]):
        """Calculate the mrr of the upstream server and reranked choices from
        the model. This only occurs if the client specified the "nboost"
        parameter in the request url or body."""
        upstream_mrr = self.calculate_mrr(correct_cids, choices)
        reranked_choices = [choices[rank] for rank in ranks]
        model_mrr = self.calculate_mrr(correct_cids, reranked_choices)
        self.record_mrrs(upstream_mrr=upstream_mrr, model_mrr=model_mrr)

    @staticmethod
    def calculate_mrr(correct_cids: List[str], choices: List[Choice]):
        """Calculate mean reciprocal rank as the first correct result index"""
        for i, choice in enumerate(choices, 1):
            if choice.cid in correct_cids:
                return 1 / i
        return 0

    def get_static_file(self, path: str) -> bytes:
        """Construct the static path of the frontend asset requested."""
        if path == '/nboost':
            asset = 'index.html'
        else:
            asset = path.replace('/nboost/', '', 1)

        static_path = self.STATIC_PATH.joinpath(asset)

        # for security reasons, make sure there is no access to other dirs
        if self.STATIC_PATH in static_path.parents and static_path.exists():
            return static_path.read_bytes()
        else:
            return self.STATIC_PATH.joinpath('404.html').read_bytes()

    def loop(self, client_socket, address):
        """Main ioloop for reranking server results to the client. Exceptions
        raised in the http parser must be reraised from __context__ because
        they are caught by the MagicStack implementation"""
        server_socket = self.set_socket()
        buffer = bytearray()
        request = Request()
        response = Response()
        log = ('%s:%s %s', *address, request)

        try:

            with HttpParserContext():
                # receive and buffer the client request
                self.client_recv(client_socket, request, buffer)
                self.logger.debug(*log)
                field, query = self.codex.parse_query(request)

                # magnify the size of the request to the server
                topk, correct_cids = self.codex.multiply_request(request)
                self.server_connect(server_socket)
                self.server_send(server_socket, request)

                # make sure server response comes back properly
                self.server_recv(server_socket, response)
                server_socket.close()
                response.unpack()

            if response.status < 300:
                # parse the choices from the magnified response
                choices = self.codex.parse_choices(response, field)
                self.record_topk_and_choices(topk=topk, choices=choices)

                # use the model to rerank the choices
                ranks = self.model_rank(query, choices)[:topk]
                self.codex.reorder_response(request, response, ranks)

                # if the "nboost" param was sent, calculate MRRs
                if correct_cids is not None:
                    self.calculate_mrrs(correct_cids, choices, ranks)

            self.client_send(request, response, client_socket)

        except FrontendRequest:
            self.logger.info(*log)

            if request.url.path == '/nboost/status':
                response.body = json.dumps(self.status, indent=2).encode()
            else:
                response.body = self.get_static_file(request.url.path)
            self.client_send(request, response, client_socket)

        except (UnknownRequest, MissingQuery):
            self.logger.warning(*log)
            self.server_connect(server_socket)

            # send the initial buffer that was used to check url path
            self.proxy_send(client_socket, server_socket, buffer)

            # stream the client socket to the server socket
            self.proxy_recv(client_socket, server_socket)
            server_socket.close()

        except Exception as exc:
            # for misc errors, send back json error msg
            self.logger.error(repr(exc), exc_info=True)
            response.body = json.dumps(dict(error=repr(exc))).encode()
            response.status = 500
            self.client_send(request, response, client_socket)

        finally:
            client_socket.close()

    def run(self):
        """Same as socket server run() but logs"""
        self.logger.critical('Upstream host is %s:%s', *self.uaddress)
        super().run()

    def close(self):
        """Close the proxy server and model"""
        self.logger.info('Closing model...')
        self.model.close()
        super().close()
