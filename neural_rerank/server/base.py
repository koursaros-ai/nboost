from ..base import BaseLogger, pfmt, pfmt_obj
from pprint import pformat
from threading import Thread, Event
from aiohttp import web_exceptions, web_routedef, web
from .handler import ServerHandler
import asyncio
import time
from typing import Dict, Tuple, Callable
from ..base.types import *
from ..base import StatefulBase


def running_avg(avg: float, new: float, n: int):
    return (avg * n + new) / n


class BaseServer(StatefulBase, Thread):
    handler = ServerHandler()

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 54001,
                 read_bytes: int = 2048,
                 status_path: str = '/status',
                 status_method: str = '*',
                 **kwargs):
        StatefulBase.__init__(self, **kwargs)
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.loop = None
        self.read_bytes = read_bytes
        self.is_ready = Event()
        self.handler.add_route(status_method, status_path)(self.status)

    def create_app(self, routes: Dict[Route, Tuple[str, str, Callable]]):
        """
        function to run a web server given a dictionary of routes

        :param routes: {Route => (method, path, function}
        :return:
        """
        raise NotImplementedError

    def state(self):
        return dict(
            host=self.host,
            port=self.port,
            ext_host=self.ext_port,
            ext_port=self.ext_port,
            read_bytes=self.read_bytes,
            is_ready=self.is_ready.is_set())

    async def status(self, request: web.BaseRequest):
        return self.handler.json_ok(self.state())

    @web.middleware
    async def middleware(self, request: web.BaseRequest, handler: Callable) -> web.Response:

        self.logger.info('RECV: %s' % request)
        self.logger.debug(pfmt(request))
        self.handler.routes[request.path]['reqs'] += 1
        start = time.time()

        try:
            response = await handler(request)
        except web_exceptions.HTTPNotFound:
            self.logger.info('NOT FOUND: %s' % request)
            response = await self.handle_not_found(request)
        except Exception as e:
            self.logger.error(e, exc_info=True)
            response = await self.handle_error(e)

        if 'pretty' in request.query:
            response.body = pfmt_obj(response.body)

        self.handler.routes[request.path]['lat'] = running_avg(
            self.handler.routes[request.path]['lat'],
            time.time() - start,
            self.handler.routes[request.path]['reqs']
        )
        self.logger.info('SEND: %s' % response)
        self.logger.debug(pfmt(response))

        return response

    async def ask(self, req: Request) -> Response:
        """ makes a request to the external host """
        raise NotImplementedError

    async def forward(self, req: Request):
        """ forward a request to the external host """
        raise NotImplementedError

    async def handle_not_found(self, request: web.BaseRequest):
        raise web.HTTPNotFound

    async def handle_error(self, e: Exception):
        return self.handler.internal_error(e)

    async def run_app(self, routes: List[web_routedef.RouteDef]) -> None:
        app = web.Application(middlewares=[self.middleware])
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

    def run(self):
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        routes = self.handler.bind_routes(self)
        self.loop.run_until_complete(self.run_app(routes))
        self.logger.critical('LISTENING: %s:%d' % (self.host, self.port))
        self.logger.info('\nROUTES:\n%s' % pformat(self.handler.routes, width=1))
        self.is_ready.set()
        self.loop.run_forever()
        self.is_ready.clear()

    def close(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()


