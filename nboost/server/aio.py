from aiohttp import web, web_exceptions, client
from typing import Callable
from ..base import *
import aiohttp


class AioHttpServer(BaseServer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.not_found_handler = None
        self.app = None

    def create_app(self, routes, not_found_handler):
        self.app = web.Application(middlewares=[self.middleware])
        for path, methods, f in routes:
            for method in methods:
                self.app.add_routes([web.route(method, path, f)])
        self.not_found_handler = not_found_handler

    async def run_app(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.runner = runner

    async def close(self):
        await self.runner.shutdown()
        await self.runner.cleanup()

    @staticmethod
    async def format_client_response(
            response: client.ClientResponse) -> Response:
        return Response(
            headers=dict(response.headers),
            body=await response.read(),
            status=response.status)

    @web.middleware
    async def middleware(self, request: web.BaseRequest,
                         handler: Callable) -> web.Response:
        try:
            self.logger.info(request)
            req = Request(
                method=request.method,
                path=request.path,
                params=dict(request.query),
                headers=dict(request.headers),
                body=await request.read())

            res = await handler(req)
            return web.Response(
                headers=res.headers,
                body=res.body,
                status=res.status)
        except web_exceptions.HTTPNotFound:
            return await self.not_found_handler(request)

    async def ask(self, req):
        async with aiohttp.request(
                req.method,
                'http://%s:%s%s' % (self.ext_host, self.ext_port, req.url),
                data=req.body,
                headers=req.headers) as response:
            return await self.format_client_response(response)

    async def forward(self, req: web.BaseRequest):
        url = 'http://%s:%s%s' % (self.ext_host, self.ext_port, req.url)
        raise web.HTTPTemporaryRedirect(url)

