from asyncio import StreamReader, StreamWriter
from typing import Callable, Coroutine
from .helpers import *
from ...base import *
import asyncio
import re


class PathNotFoundError(Exception):
    pass


class LoopServer(BaseServer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.routes = None
        self.not_found_handler = None

    def get_handler(self, path: str, method: str):
        for path_pattern, methods, f in self.routes:
            if re.match(path_pattern, path) and method in methods:
                return f
        raise PathNotFoundError

    def create_app(self, routes, not_found_handler: Callable):
        self.routes = routes
        self.not_found_handler = not_found_handler

    @staticmethod
    async def pipe(reader, writer, start: bytes = None):
        try:
            if start:
                writer.write(start)
            while not reader.at_eof():
                writer.write(await reader.read(2048))
        finally:
            writer.close()

    async def open_server_connection(self):
        return await asyncio.open_connection(self.ext_host, self.ext_port)

    async def proxy(self,
                    client_reader: StreamReader,
                    client_writer: StreamWriter,
                    start: bytes = None):

        server_reader, server_writer = await self.open_server_connection()
        pipe1 = self.pipe(client_reader, server_writer, start=start)
        pipe2 = self.pipe(server_reader, client_writer)
        await asyncio.gather(pipe1, pipe2)

    async def handle_client(self, client_reader, client_writer):
        try:

            buffer = await client_reader.read(2048)
            proxy = self.proxy(client_reader, client_writer, start=buffer)

            try:
                method, path, version = buffer.split(CRLF)[0].split()
                self.logger.info(b'<%s %s %s>' % (version, method, path))
                handler = self.get_handler(path, method)
                should_proxy = False

            # except ValueError as e:
            #     self.logger.info('Could not parse http request.')
            #     should_proxy = True
            except PathNotFoundError:
                self.logger.info('<No handler found>')
                should_proxy = True
            else:
                if len(buffer) == 2048 and not client_reader.at_eof():
                    buffer += await client_reader.read()

                req = bytes_to_request(buffer)
                res = await handler(req)
                response = response_to_bytes(res)
                client_writer.write(response)

            if should_proxy:
                await self.not_found_handler(proxy)

        finally:
            client_writer.close()

    async def run_app(self):
        await asyncio.start_server(self.handle_client, self.host, self.port)

    async def ask(self, req):
        """ Make the magnified request to the server api. """
        server_reader, server_writer = await self.open_server_connection()
        request = request_to_bytes(req)
        server_writer.write(request)
        buffer = b''
        while True:
            b = await server_reader.read(2048)
            buffer += b
            if len(b) != 2048:
                break
        return bytes_to_response(buffer)

    async def forward(self, ctx: Coroutine) -> None:
        await ctx

    async def close(self):
        pass
