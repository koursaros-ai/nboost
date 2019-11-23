"""NBoost Proxy Class"""

import json
import socket
from typing import Type, List, Tuple
from threading import Thread, Event, get_ident
from functools import partial
from httptools import HttpParserError, HttpRequestParser, HttpResponseParser
from ..base import set_logger, BaseModel, BaseProtocol
from ..base.handler import BaseHandler, RequestHandler, ResponseHandler
from ..base.helpers import TimeContext
from ..base.types import Request, Response
from ..base.exceptions import *


class SocketServer(Thread):
    """Base Socket Server class for the proxy"""
    def __init__(self, host: str = 'localhost', port: int = 8000,
                 backlog: int = 100, workers: int = 10, **kwargs):
        super().__init__()
        self.address = (host, port)
        self.backlog = backlog
        self.workers = workers
        self.is_ready = Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger = set_logger(self.__class__.__name__)

    def worker(self):
        """Socket loop for each worker"""
        try:
            while True:
                self.loop(*self.sock.accept())

        except OSError:
            self.logger.debug('Closing worker %s...', get_ident())

    def loop(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Loop for each worker to execute when it receives client conn"""

    def run(self):
        """Run the socket server main thread"""
        self.sock.bind(self.address)
        self.sock.listen(self.backlog)
        threads = []

        try:
            self.logger.info('Starting %s workers...', self.workers)
            for _ in range(self.workers):
                thread = Thread(target=self.worker)
                thread.start()
                threads.append(thread)

            self.is_ready.set()
            self.logger.critical('Listening on %s:%s...', *self.address)
            for thread in threads:
                thread.join()

        finally:
            self.logger.critical('Closed %s:%s...', *self.address)

    def close(self):
        """Close the serving socket"""
        self.logger.info('Closing %s:%s...', *self.address)
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.join()


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
    :param protocol: uninitialized protocol class
    """
    time_context = TimeContext()

    def __init__(self, model: Type[BaseModel], protocol: Type[BaseProtocol],
                 uhost: str = 'localhost', uport: int = 9200,
                 bufsize: int = 2048, multiplier: int = 5, field: str = 'text',
                 verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = kwargs
        self.uaddress = (uhost, uport)
        self.bufsize = bufsize
        self.topk_stats = dict(avg=0.0, trips=0)
        self.choices_stats = dict(avg=0.0, trips=0)
        self.logger = set_logger(model.__name__, verbose=verbose)

        # pass command line arguments to instantiate each component
        self.model = model(verbose=verbose, **kwargs)
        self.protocol = partial(protocol, multiplier, field)

    def recv(self, handler: BaseHandler, in_socket: socket.socket,
             out_socket: socket.socket = None, buffer: dict = None):
        """Receive data and optionally send to output socket or buffer"""
        while not handler.is_done:
            data = in_socket.recv(self.bufsize)
            if buffer is not None:
                buffer['data'] += data
            if out_socket is not None:
                out_socket.send(data)
            handler.feed(data)

    @time_context
    def proxy_send(self, client_socket, server_socket, buffer: dict):
        """Send buffered request to server and receive the rest of the original
        client request"""
        handler = BaseHandler(HttpRequestParser)
        server_socket.send(buffer['data'])
        handler.feed(buffer['data'])
        self.recv(handler, client_socket, server_socket)

    @time_context
    def proxy_recv(self, client_socket, server_socket):
        """Receive the proxied response and pipe to the client"""
        handler = BaseHandler(HttpResponseParser)
        self.recv(handler, server_socket, client_socket)

    @time_context
    def client_recv(self, client_socket: socket.socket,
                    handler: RequestHandler, buffer: dict):
        """Receive client request and pipe to buffer in case of exceptions"""
        self.recv(handler, client_socket, buffer=buffer)

    @staticmethod
    @time_context
    def server_send(server_socket, request: Request):
        """Send magnified request to the server"""
        server_socket.send(request.prepare())

    @time_context
    def server_recv(self, server_socket, handler: ResponseHandler):
        """Receive magnified request from the server"""
        self.recv(handler, server_socket)

    @staticmethod
    @time_context
    def client_send(client_socket, response: Response):
        """Send the ranked results to the client"""
        client_socket.send(response.prepare())

    @time_context
    def model_rank(self, topk, query: str, choices: List[str]) -> List[int]:
        """Rank the query and choices and return the argsorted indices"""
        self.topk_stats['avg'] = self.time_context.mean(
            self.topk_stats['avg'],
            topk, self.topk_stats['trips']
        )
        self.choices_stats['avg'] = self.time_context.mean(
            self.choices_stats['avg'],
            len(choices), self.choices_stats['trips']
        )
        self.topk_stats['trips'] += 1
        self.choices_stats['trips'] += 1

        return self.model.rank(query, choices)

    @time_context
    def server_connect(self, server_socket: socket.socket) -> None:
        """Connect proxied server socket"""
        try:
            server_socket.connect(self.uaddress)
        except ConnectionRefusedError:
            raise UpstreamConnectionError(*self.uaddress)

    @property
    def status(self) -> dict:
        """Return status dictionary in the case of a status request"""
        return dict(topk=self.topk_stats, choices=self.choices_stats,
                    multiplier=self.protocol().multiplier,
                    times=self.time_context.record,
                    description='NBoost, for search ranking.')

    def loop(self, client_socket, address):
        """Main ioloop for reranking server results to the client. Exceptions
        raised in the http parser must be reraised from __context__ because
        they are caught by the MagicStack implementation"""
        protocol = self.protocol()
        server_socket = socket.socket()
        buffer = dict(data=bytes())
        exception = None

        try:
            self.server_connect(server_socket)
            self.client_recv(client_socket, RequestHandler(protocol), buffer)
            self.server_send(server_socket, protocol.request)
            self.server_recv(server_socket, ResponseHandler(protocol))
            ranks = self.model_rank(protocol.topk, protocol.query, protocol.choices)
            protocol.on_rank(ranks)

        except HttpParserError as exc:
            exception = exc.__context__

        except Exception as exc:
            exception = exc

        try:
            log = '{}:{}: {}'.format(*address, protocol.request)
            if exception is None:
                self.logger.debug(log)
            else:
                self.logger.warning('%s: %s', type(exception).__name__, log)
                raise exception

        except StatusRequest:
            protocol.response.body = json.dumps(self.status, indent=2).encode()
            protocol.response.encode()

        except (UnknownRequest, MissingQuery):
            self.proxy_send(client_socket, server_socket, buffer)
            self.proxy_recv(client_socket, server_socket)

        except ResponseException:
            # allow the body to be sent back to the client
            pass

        except UpstreamConnectionError as exc:
            self.logger.error("Couldn't connect to server %s:%s...", *exc.args)
            protocol.on_error(exc)

        except Exception as exc:
            self.logger.error(repr(exc), exc_info=True)
            protocol.on_error(exc)

        finally:
            self.client_send(client_socket, protocol.response)
            client_socket.close()
            server_socket.close()

    def run(self):
        """Same as socket server run() but logs"""
        self.logger.critical('Upstream host is %s:%s', *self.uaddress)
        super().run()

    def close(self):
        """Close the proxy server and model"""
        self.logger.info('Closing model...')
        self.model.close()
        super().close()
