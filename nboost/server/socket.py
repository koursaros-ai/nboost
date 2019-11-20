from httptools import HttpRequestParser, HttpResponseParser, parse_url, HttpParserError
from threading import Thread
from ..base import *
import socket
import re


class HandlerNotFoundError(Exception):
    pass


class HttpProtocol:
    def __init__(self):
        self.save = True
        self.complete = False
        self.path = None
        self.headers = dict()
        self.body = bytes()
        self.params = dict()

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        if self.save:
            url = parse_url(url)
            self.path = url.path.decode()
            query = url.query
            self.params = dict(parse_qsl(query.decode())) if query else {}

    def on_header(self, name: bytes, value: bytes):
        if self.save:
            self.headers[name.decode()] = value.decode()

    def on_headers_complete(self):
        pass

    def on_body(self, body: bytes):
        if self.save:
            self.body += body

    def on_message_complete(self):
        self.complete = True

    def on_chunk_header(self):
        pass

    def on_chunk_complete(self):
        pass

    def on_status(self, status: bytes):
        pass


class SocketServer(SyncServer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workers = 5
        self.backlog = 5
        self.not_found_handler = None
        self.routes = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def create_app(self, routes, not_found_handler):
        self.routes = routes
        self.not_found_handler = not_found_handler

    def get_handler(self, path: str, method: str):
        for path_pattern, methods, f in self.routes:
            if re.match(path_pattern, path) and method in methods:
                return f
        raise HandlerNotFoundError

    def run_app(self):
        self.sock.bind((self.host, self.port))
        self.logger.critical('WORKERS: %s' % self.workers)

        # put the socket into listening mode
        self.sock.listen(self.backlog)
        self.is_ready.set()

        threads = []
        try:
            for i in range(self.workers):
                t = Thread(target=self.ioloop)
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        finally:
            self.sock.close()

    def ioloop(self):
        is_ioloop = True
        while is_ioloop:
            try:
                client_socket, address = self.sock.accept()
                self.logger.info('Request from {}:{}'.format(*address))
                self.handle_client(client_socket)
            except ConnectionAbortedError:
                self.logger.warning('Connection aborted')
                is_ioloop = False

    def handle_client(self, client_socket: socket.socket):
        buffer = bytes()
        handler = None
        protocol = HttpProtocol()
        parser = HttpRequestParser(protocol)
        try:
            while not protocol.complete:
                data = client_socket.recv(1024)
                buffer += data
                parser.feed_data(data)
                if protocol.path and handler is None:
                    handler = self.get_handler(protocol.path,
                                               parser.get_method().decode())
        except HandlerNotFoundError:
            self.logger.info('Not found')
            self.not_found_handler(client_socket, protocol, parser, buffer)
        except HttpParserError:
            should_proxy = True
        else:
            request = Request(headers=protocol.headers,
                              body=protocol.body, path=protocol.path,
                              params=protocol.params,
                              method=parser.get_method().decode())
            self.logger.info(request)
            response = handler(request)
            client_socket.send(prepare_response(response))
        finally:
            client_socket.close()

    def close(self):
        self.sock.close()

    def ask(self, request: Request):
        protocol = HttpProtocol()
        parser = HttpResponseParser(protocol)
        server_socket = socket.socket()
        server_socket.connect((self.ext_host, self.ext_port))
        server_socket.send(prepare_request(request))

        while not protocol.complete:
            parser.feed_data(server_socket.recv(1024))

        response = Response(headers=protocol.headers, body=protocol.body,
                            status=parser.get_status_code())
        return response

    def forward(self, client_socket: socket.socket, protocol: HttpProtocol,
                parser: HttpRequestParser, buffer: bytes):
        server_socket = socket.socket()
        server_socket.connect((self.ext_host, self.ext_port))
        server_socket.send(buffer)
        protocol.save = False
        try:
            while not protocol.complete:
                data = client_socket.recv(1024)
                parser.feed_data(data)
                server_socket.send(data)

            protocol = HttpProtocol()
            parser = HttpResponseParser(protocol)
            while not protocol.complete:
                data = server_socket.recv(1024)
                parser.feed_data(data)
                client_socket.send(data)
        finally:
            client_socket.close()
            server_socket.close()
