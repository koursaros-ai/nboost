from httptools import HttpRequestParser, HttpResponseParser, HttpParserError
from .helpers import HttpProtocol, prepare_request, prepare_response
from asyncio import StreamReader, StreamWriter
from typing import Callable
from ...base import *
import asyncio
import gzip
import re


class HandlerNotFoundError(Exception):
    pass


class LoopServer(BaseServer):

    def __init__(self, read_bytes: int = 2048, **kwargs):
        super().__init__(**kwargs)
        self.routes = None
        self.server = None
        self.not_found_handler = None
        self.read_bytes = read_bytes

    def get_handler(self, path: str, method: str):
        for path_pattern, methods, f in self.routes:
            if re.match(path_pattern, path) and method in methods:
                return f
        raise HandlerNotFoundError

    def create_app(self, routes, not_found_handler: Callable):
        self.routes = routes
        self.not_found_handler = not_found_handler

    async def pipe(self, reader, writer):
        try:
            while not reader.at_eof():
                writer.write(await reader.read(self.read_bytes))
        finally:
            if not self.loop.is_closed():
                writer.close()

    async def open_server_connection(self):
        return await asyncio.open_connection(self.ext_host, self.ext_port)

    async def handle_client(self, client_reader, client_writer):
        buffer = bytes()
        should_proxy = True
        request = Request()
        protocol = HttpProtocol(request)
        parser = HttpRequestParser(protocol)
        try:
            while request.path is None:
                data = await client_reader.read(self.read_bytes)
                buffer += data
                parser.feed_data(data)

            request.method = parser.get_method().decode()

            handler = self.get_handler(request.path, request.method)
            self.logger.info('%s -> %s()' % (request, handler.__name__))

            while not protocol.complete:
                data = await client_reader.read(self.read_bytes)
                buffer += data
                parser.feed_data(data)

            if request.is_gzip:
                request.ungzip()

            response = await handler(request)

            if response.is_gzip:
                response.gzip()

            client_writer.write(prepare_response(response))

        except HandlerNotFoundError:
            self.logger.info('No handler found: %s' % request)
        except HttpParserError as e:
            self.logger.warning('%s: %s' % (e, request))
        else:
            should_proxy = False
        finally:
            if should_proxy:
                await self.not_found_handler(client_reader,
                                             client_writer,
                                             buffer)
            if not self.loop.is_closed():
                client_writer.close()

    async def run_app(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

    async def ask(self, request: Request) -> Response:
        """ Make the magnified request to the server api. """
        if request.is_gzip:
            request.gzip()

        server_reader, server_writer = await self.open_server_connection()
        server_writer.write(prepare_request(request))
        response = Response()
        protocol = HttpProtocol(response)
        parser = HttpResponseParser(protocol)
        while not protocol.complete:
            parser.feed_data(await server_reader.read(self.read_bytes))
        server_writer.close()
        response.status = parser.get_status_code()

        if response.is_gzip:
            response.ungzip()

        return response

    async def forward(self,
                      client_reader: StreamReader,
                      client_writer: StreamWriter, buffer: bytes):

        server_reader, server_writer = await self.open_server_connection()
        server_writer.write(buffer)
        pipe1 = self.pipe(client_reader, server_writer)
        pipe2 = self.pipe(server_reader, client_writer)
        await asyncio.gather(pipe1, pipe2)

    async def close(self):
        self.server.close()
