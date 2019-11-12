from aiohttp import web, web_exceptions, client
from urllib.parse import urlencode
from typing import Callable
from ..base import *
import aiohttp


class AioHttpServer(BaseServer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error_handler = None
        self.not_found_handler = None
        self.app = None

    def create_app(self, routes, not_found_handler):
        self.app = web.Application(middlewares=[self.middleware])
        for path_methods, f in routes:
            for path, methods in path_methods.items():
                for method in methods:
                    self.app.add_routes([web.route(method, path, f)])
        self.not_found_handler = not_found_handler

    async def run_app(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.logger.critical('LISTENING: %s:%d' % (self.host, self.port))
        self.runner = runner

    async def close(self):
        self.logger.critical('SHUTDOWN: %s:%d' % (self.host, self.port))
        await self.runner.shutdown()
        await self.runner.cleanup()

    @staticmethod
    async def format_client_response(
            response: client.ClientResponse) -> Response:
        headers = dict(response.headers)
        headers['Content-Type'] = 'application/json'
        return Response(headers, await response.read(), response.status)

    @web.middleware
    async def middleware(self, request: web.BaseRequest,
                         handler: Callable) -> web.Response:
        try:
            self.logger.info(request)
            req = Request(
                request.method,
                request.path,
                dict(request.headers),
                dict(request.query),
                await request.read())
            res = await handler(req)
            return web.Response(
                headers=res.headers,
                body=res.body,
                status=res.status)
        except web_exceptions.HTTPNotFound:
            return await self.not_found_handler(request)

    async def ask(self, req):
        url = 'http://%s:%s%s?%s' % (
            self.ext_host, self.ext_port, req.path, urlencode(req.params))
        headers = dict(req.headers)
        headers['Content-Type'] = 'application/json'

        async with aiohttp.request(req.method, url, data=req.body,
                                   headers=headers) as response:
            return await self.format_client_response(response)

    async def forward(self, req: web.Request) -> web.Response:
        url = 'http://%s:%s' % (self.ext_host, self.ext_port)
        async with aiohttp.ClientSession() as session:
            headers = dict(req.headers)
            headers['Content-Type'] = 'application/json'
            async with session.request(
                    req.method,
                    url + req.path + '?' + req.query_string,
                    headers=headers,
                    data=await req.read()) as resp:

                return web.Response(
                    status=resp.status,
                    body=await resp.content.read())
