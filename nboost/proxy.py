"""NBoost Proxy Class"""

from typing import Type, List, Tuple
from contextlib import suppress
import socket
import re
from httptools import HttpParserError
from nboost.protocol import HttpProtocol
from nboost.stats import ClassStatistics
from nboost.models.base import BaseModel
from nboost.server import SocketServer
from nboost.logger import set_logger
from nboost.maps import CONFIG_MAP
from nboost import PKG_PATH
from nboost.helpers import (
    prepare_response,
    prepare_request,
    get_jsonpath,
    set_jsonpath,
    dump_json,
    flatten)
from nboost.exceptions import (
    UpstreamConnectionError,
    FrontendRequest,
    UnknownRequest,
    MissingQuery)


class HttpParserContext:
    """Context that reraises the __context__ of an HttpParserError"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, HttpParserError) and exc_val.__context__:
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

    def __init__(self, model: Type[BaseModel], config: str = 'elasticsearch',
                 verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.logger = set_logger(model.__name__, verbose=verbose)

        # pass command line arguments to instantiate the model
        self.model = model(verbose=verbose, **kwargs)

        # these are global parameters that are overrided by nboost json key
        self.config = {'model': model.__name__, **CONFIG_MAP[config], **kwargs}

    def on_client_request_url(self, url: dict):
        """Method for screening the url path from the client request"""
        if url['path'].startswith('/nboost'):
            raise FrontendRequest

        if not re.match(self.config['capture_path'], url['path']):
            raise UnknownRequest

    def get_protocol(self) -> HttpProtocol:
        """Return a configured http protocol parser."""
        return HttpProtocol(self.config['bufsize'])

    @stats.time_context
    def proxy_send(self, client_socket, server_socket, buffer: bytearray):
        """Send buffered request to server and receive the rest of the original
        client request"""
        protocol = self.get_protocol()
        protocol.set_request_parser()
        server_socket.send(buffer)
        protocol.feed(buffer)
        protocol.add_data_hook(server_socket.send)
        protocol.recv(client_socket)

    @stats.time_context
    def proxy_recv(self, client_socket, server_socket):
        """Receive the proxied response and pipe to the client"""
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.add_data_hook(client_socket.send)
        protocol.recv(server_socket)

    @stats.time_context
    def client_recv(self, client_socket, request: dict, buffer: bytearray):
        """Receive client request and pipe to buffer in case of exceptions"""
        protocol = self.get_protocol()
        protocol.set_request_parser()
        protocol.set_request(request)
        protocol.add_data_hook(buffer.extend)
        protocol.add_url_hook(self.on_client_request_url)
        protocol.recv(client_socket)

    @staticmethod
    @stats.time_context
    def server_send(server_socket: socket.socket, request: dict):
        """Send magnified request to the server"""
        server_socket.send(prepare_request(request))

    @stats.time_context
    def server_recv(self, server_socket: socket.socket, response: dict):
        """Receive magnified request from the server"""
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.set_response(response)
        protocol.recv(server_socket)

    @staticmethod
    @stats.time_context
    def client_send(request: dict, response: dict, client_socket):
        """Send the ranked results to the client"""
        client_socket.send(prepare_response(request, response))

    @stats.time_context
    def model_rank(self, query: str, choices: List[str]) -> List[int]:
        """Rank the query and choices and return the argsorted indices"""
        return self.model.rank(query, choices)

    @stats.vars_context
    def record_topk_and_choices(self, topk: int = None, choices: list = None):
        """Add topk and choices to the running statistical averages"""

    @stats.vars_context
    def record_mrrs(self, upstream_mrr: float = None, model_mrr: float = None):
        """Add the upstream mrr, model mrr, and search boost to the stats"""
        with suppress(ZeroDivisionError):
            var = self.stats.record['vars']
            var['search_boost'] = {
                'avg': var['model_mrr']['avg'] / var['upstream_mrr']['avg']}

    @stats.time_context
    def server_connect(self, server_socket: socket.socket):
        """Connect proxied server socket"""
        uaddress = (self.config['uhost'], self.config['uport'])
        try:
            server_socket.connect(uaddress)
        except ConnectionRefusedError:
            raise UpstreamConnectionError('Connect error for %s:%s' % uaddress)

    @property
    def status(self) -> dict:
        """Return status dictionary in the case of a status request"""
        return {**self.config, **self.stats.record,
                'description': 'NBoost, for search ranking.'}

    def calculate_mrrs(self, true_cids: List[str], cids: List[str],
                       ranks: List[int]):
        """Calculate the mrr of the upstream server and reranked choices from
        the model. This only occurs if the client specified the "nboost"
        parameter in the request url or body."""
        upstream_mrr = self.calculate_mrr(true_cids, cids)
        reranked_cids = [cids[rank] for rank in ranks]
        model_mrr = self.calculate_mrr(true_cids, reranked_cids)
        self.record_mrrs(upstream_mrr=upstream_mrr, model_mrr=model_mrr)

    @staticmethod
    def calculate_mrr(correct: list, guesses: list):
        """Calculate mean reciprocal rank as the first correct result index"""
        for i, guess in enumerate(guesses, 1):
            if guess in correct:
                return 1 / i
        return 0

    def get_static_file(self, path: str) -> bytes:
        """Construct the static path of the frontend asset requested and return
        the raw file."""
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

    def loop(self, client_socket: socket.socket, address: Tuple[str, str]):
        """Main ioloop for reranking server results to the client. Exceptions
        raised in the http parser must be reraised from __context__ because
        they are caught by the MagicStack implementation"""
        server_socket = self.set_socket()
        buffer = bytearray()
        request = {'version': 'HTTP/1.1', 'headers': {}}
        response = {'version': 'HTTP/1.1', 'headers': {}}
        log = ('<Request from %s:%s>', *address)

        try:
            self.server_connect(server_socket)

            with HttpParserContext():
                # receive and buffer the client request
                self.client_recv(client_socket, request, buffer)
                self.logger.debug(*log)

                # combine runtime configs and preset configs
                configs = {**self.config, **request.get('nboost', {})}

                queries = get_jsonpath(request, configs['query_path'])
                query = configs['delim'].join(queries)

                # magnify the size of the request to the server
                topks = get_jsonpath(request, configs['topk_path'])
                topk = int(topks[0]) if topks else configs['default_topk']
                true_cids = get_jsonpath(request, configs['true_cids_path'])
                new_topk = topk * configs['multiplier']
                set_jsonpath(request, configs['topk_path'], new_topk)
                self.server_send(server_socket, request)

                # make sure server response comes back properly
                self.server_recv(server_socket, response)

            if response['status'] < 300:
                # parse the choices from the magnified response
                choices = get_jsonpath(response, configs['choices_path'])
                choices = flatten(choices)
                cids = get_jsonpath(response, configs['cids_path'])
                # choices = self.codex.parse_choices(response, field)
                self.record_topk_and_choices(topk=topk, choices=choices)

                # use the model to rerank the choices
                cvalues = get_jsonpath(response, configs['cvalues_path'])
                ranks = self.model_rank(query, cvalues)[:topk]
                reranked = [choices[rank] for rank in ranks]
                set_jsonpath(response, configs['choices_path'], reranked)

                # if the "nboost" param was sent, calculate MRRs
                if true_cids is not None:
                    self.calculate_mrrs(true_cids, cids, ranks)

            self.client_send(request, response, client_socket)

        except FrontendRequest:
            self.logger.info(*log)

            response['headers'] = {}

            if request['url']['path'] == '/nboost/status':
                response['body'] = self.status
            else:
                response['body'] = self.get_static_file(request['url']['path'])

            request['url']['query']['pretty'] = True
            response['status'] = 200
            self.client_send(request, response, client_socket)

        except (UnknownRequest, MissingQuery):
            self.logger.warning(*log)

            # send the initial buffer that was used to check url path
            self.proxy_send(client_socket, server_socket, buffer)

            # stream the client socket to the server socket
            self.proxy_recv(client_socket, server_socket)

        except Exception as exc:
            # for misc errors, send back json error msg
            self.logger.error(repr(exc), exc_info=True)
            response['body'] = {'error': repr(exc)}
            response['status'] = 500
            self.client_send(request, response, client_socket)

        finally:
            client_socket.close()
            server_socket.close()

    def run(self):
        """Same as socket server run() but logs"""
        self.logger.info(dump_json(self.config, indent=4).decode())
        super().run()

    def close(self):
        """Close the proxy server and model"""
        self.logger.info('Closing model...')
        self.model.close()
        super().close()
