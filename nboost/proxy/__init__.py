from threading import Thread, Event, get_ident
from httptools import HttpParserError, HttpRequestParser, HttpResponseParser
from typing import Type
from ..base import *
import socket
import json
import time


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
        ident = get_ident()
        try:
            while True:
                client_socket, address = self.sock.accept()
                self.logger.debug('{}: Request {}:{}'.format(ident, *address))
                self.loop(client_socket)

        except (ConnectionAbortedError, OSError):
            self.logger.info('Stopping worker %s' % get_ident())

    def loop(self, client_socket: socket.socket) -> None:
        raise NotImplementedError

    def run(self):
        self.sock.bind(self.address)
        self.sock.listen(self.backlog)
        self.logger.info('Starting %s workers...' % self.workers)
        self.logger.critical('Listening on %s:%s...' % self.address)
        threads = []

        try:
            for i in range(self.workers):
                t = Thread(target=self.worker)
                t.start()
                threads.append(t)

            self.is_ready.set()

            for t in threads:
                t.join()

        finally:
            self.sock.close()

    def close(self):
        self.sock.close()
        self.join()


class Proxy(SocketServer):
    def __init__(self, model: Type[BaseModel], protocol: Type[BaseProtocol],
                 uhost: str = 'localhost', uport: int = 9200,
                 bufsize: int = 2048, multiplier: int = 5, field: str = 'text',
                 **kwargs):
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
        self.uhost = uhost
        self.uport = uport
        self.bufsize = bufsize
        self.multiplier = multiplier
        self.field = field
        self.logger = set_logger(model.__name__)

        # pass command line arguments to instantiate each component
        self.model = model(**kwargs)
        self.Protocol = protocol

        # for status requests
        self.status = dict(bench={}, description='NBoost, for search ranking.')

    def loop(self, client_socket: socket.socket):
        protocol = self.Protocol(self.multiplier, self.field)
        request_handler = RequestHandler(protocol)
        response_handler = ResponseHandler(protocol)
        server_socket = socket.socket()
        time_context = TimeContext(self.status['bench'])
        unhandled = None

        with time_context('server_connect'):
            server_socket.connect((self.uhost, self.uport))

        try:
            with time_context('client_recv'):
                while not request_handler.is_done:
                    request_handler.feed(client_socket.recv(self.bufsize))

            self.logger.debug(protocol.request)

            with time_context('server_send'):
                request = protocol.request.prepare()
                server_socket.send(request)

            with time_context('server_recv'):
                while not response_handler.is_done:
                    response_handler.feed(server_socket.recv(self.bufsize))

            with time_context('model_rank'):
                import pdb
                pdb.set_trace()
                ranks = self.model.rank(protocol.query, protocol.choices)

            protocol.on_rank(ranks)
            response = protocol.response.prepare()

            with time_context('client_send'):
                client_socket.send(response)

        except HttpParserError as e:
            if isinstance(e.__context__, StatusRequest):
                self.logger.debug(protocol.request)
                protocol.response.body = json.dumps(self.status, indent=2).encode()
                response = protocol.response.prepare()
                client_socket.send(response)

            elif isinstance(e.__context__, UnknownRequest):
                self.logger.debug(protocol.request)
                proxy_request_handler = BaseHandler(HttpRequestParser)
                proxy_request_handler.feed(request_handler.buffer)
                proxy_response_handler = BaseHandler(HttpResponseParser)

                with time_context('proxy_send'):
                    server_socket.send(request_handler.buffer)
                    while not proxy_request_handler.is_done:
                        data = client_socket.recv(self.bufsize)
                        proxy_request_handler.feed(data)
                        server_socket.send(data)

                with time_context('proxy_recv'):
                    while not proxy_response_handler.is_done:
                        data = server_socket.recv(self.bufsize)
                        proxy_response_handler.feed(data)
                        client_socket.send(data)

                server_socket.close()
            else:
                self.logger.error(repr(e.__context__), exc_info=True)
                unhandled = e.__context__

        except Exception as e:
            self.logger.error(repr(e), exc_info=True)
            unhandled = e

        finally:
            if unhandled:
                protocol.on_error(unhandled)
                response = protocol.response.prepare()
                client_socket.send(response)

            if client_socket:
                client_socket.close()
            if server_socket:
                server_socket.close()


class TimeContext:
    """Records the time within a with() context and stores the latency (in ms)
     within a record (dict)"""
    def __init__(self, record: dict):
        self.record = record
        self.last = None
        self.key = None

    def __call__(self, key: str):
        self.key = key
        return self

    def __enter__(self):
        self.last = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        r = self.record.get(self.key, dict(avg=0, trips=0))
        avg, trips = r['avg'], r['trips']
        avg *= trips
        avg += (time.perf_counter() - self.last) * 1000
        trips += 1
        avg /= trips
        self.record[self.key] = dict(avg=avg, trips=trips)


