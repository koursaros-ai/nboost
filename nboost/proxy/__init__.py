from httptools import HttpParserError, HttpRequestParser, HttpResponseParser
from typing import Type, List, Tuple
from threading import Thread, Event, get_ident
from abc import abstractmethod
from ..base import *
import socket
import json


class SocketServer(Thread):
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
        try:
            while True:
                self.loop(*self.sock.accept())

        except (ConnectionAbortedError, OSError):
            self.logger.info('Closing worker %s...' % get_ident())

    @abstractmethod
    def loop(self, client_socket: socket.socket, address: Tuple[str, int]):
        pass

    def run(self):
        self.sock.bind(self.address)
        self.sock.listen(self.backlog)
        threads = []

        try:
            self.logger.info('Starting %s workers...' % self.workers)
            for _ in range(self.workers):
                t = Thread(target=self.worker)
                t.start()
                threads.append(t)

            self.is_ready.set()
            self.logger.critical('Listening on %s:%s...' % self.address)
            for t in threads:
                t.join()

        finally:
            self.logger.critical('Closed %s:%s...' % self.address)

    def close(self):
        self.logger.info('Closing %s:%s...' % self.address)
        self.sock.close()
        self.join()


class Proxy(SocketServer):
    time_context = TimeContext()

    def __init__(self, model: Type[BaseModel], protocol: Type[BaseProtocol],
                 uhost: str = 'localhost', uport: int = 9200,
                 bufsize: int = 2048, multiplier: int = 5, field: str = 'text',
                 verbose: bool = False, **kwargs):
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
        super().__init__()
        self.kwargs = kwargs
        self.uaddress = (uhost, uport)
        self.bufsize = bufsize
        self.multiplier = multiplier
        self.field = field
        self.logger = set_logger(model.__name__, verbose=verbose)

        # pass command line arguments to instantiate each component
        self.model = model(verbose=verbose, **kwargs)
        self.Protocol = protocol

    def connect_sockets(self, handler: BaseHandler,
                        in_socket: socket.socket,
                        out_socket: socket.socket = None,
                        buffer: dict = None):
        while not handler.is_done:
            data = in_socket.recv(self.bufsize)
            if buffer is not None:
                buffer['data'] += data
            if out_socket is not None:
                out_socket.send(data)
            handler.feed(data)

    @time_context
    def proxy_send(self, client_socket, server_socket, buffer: dict):
        handler = BaseHandler(HttpRequestParser)
        server_socket.send(buffer['data'])
        handler.feed(buffer['data'])
        self.connect_sockets(handler, client_socket, server_socket)

    @time_context
    def proxy_recv(self, client_socket, server_socket):
        handler = BaseHandler(HttpResponseParser)
        self.connect_sockets(handler, server_socket, client_socket)

    @time_context
    def client_recv(self, client_socket: socket.socket,
                    handler: RequestHandler, buffer: dict):
        self.connect_sockets(handler, client_socket, buffer=buffer)

    @time_context
    def server_recv(self, server_socket, handler: ResponseHandler):
        self.connect_sockets(handler, server_socket)

    @time_context
    def server_send(self, server_socket, request: Request):
        server_socket.send(request.prepare())

    @time_context
    def client_send(self, client_socket, response: Response):
        client_socket.send(response.prepare())

    @time_context
    def model_rank(self, query: str, choices: List[str]) -> List[int]:
        return self.model.rank(query, choices)

    @time_context
    def server_connect(self) -> socket.socket:
        server_socket = socket.socket()
        server_socket.connect(self.uaddress)
        return server_socket

    @property
    def status(self) -> dict:
        return dict(bench=self.time_context.record,
                    description='NBoost, for search ranking.')

    def loop(self, client_socket, address):
        protocol = self.Protocol(self.multiplier, self.field)
        server_socket = self.server_connect()
        buffer = dict(data=bytes())
        exc = None

        try:
            self.client_recv(client_socket, RequestHandler(protocol), buffer)
            self.server_send(server_socket, protocol.request)
            self.server_recv(server_socket, ResponseHandler(protocol))
            ranks = self.model_rank(protocol.query, protocol.choices)
            protocol.on_rank(ranks)

        except HttpParserError as e:
            exc = e.__context__

        except Exception as e:
            exc = e

        try:
            log = '{}:{}: {}'.format(*address, protocol.request)
            if exc is None:
                self.logger.debug(log)
            else:
                self.logger.warning('%s: %s' % (type(exc).__name__, log))
                raise exc
        except StatusRequest:
            protocol.response.body = json.dumps(self.status, indent=2).encode()

        except (UnknownRequest, MissingQuery):
            self.proxy_send(client_socket, server_socket, buffer)
            self.proxy_recv(client_socket, server_socket)

        except Exception as e:
            self.logger.error(repr(e), exc_info=True)
            protocol.on_error(e)

        finally:
            self.client_send(client_socket, protocol.response)
            client_socket.close()
            server_socket.close()





