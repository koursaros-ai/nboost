from ..base import BaseLogger
from pprint import pformat
from multiprocessing import Process, Event
from aiohttp import web_exceptions, web_routedef, web
from typing import List, Coroutine, Callable
from .handler import ServerHandler
import asyncio


class BaseServer(BaseLogger, Process):
    handler = ServerHandler()

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 read_bytes: int = 2048,
                 status_path: str = '/status',
                 status_method: str = '*',
                 **kwargs):
        BaseLogger.__init__(self, **kwargs)
        Process.__init__(self)
        self.host = host
        self.port = port
        self.read_bytes = read_bytes
        self.is_ready = Event()
        self.handler.add_route(status_method, status_path)(self.status)

    @handler.add_state
    def _host(self):
        return self.host

    @handler.add_state
    def _port(self):
        return self.port

    @handler.add_state
    def _read_bytes(self):
        return self.read_bytes

    @handler.add_state
    def ready(self):
        return self.is_ready.is_set()

    @property
    def state(self):
        return {self.__name__: self.handler.bind_states(self)}

    async def status(self, request: web.BaseRequest):
        return self.handler.json_ok(self.state)

    async def create_app(self,
                         loop: asyncio.AbstractEventLoop,
                         routes: List[web_routedef.RouteDef]) -> None:
        app = web.Application(middlewares=[self.middleware])
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

    @web.middleware
    async def middleware(self,
                         request: web.BaseRequest,
                         handler: Callable) -> web.Response:
        self.logger.error(request)
        self.logger.error(handler)
        try:
            response = await handler(request)
        except web_exceptions.HTTPNotFound:
            response = await self.handle_not_found(request)
        except Exception as ex:
            response = self.handle_error(ex)

        if 'pretty' in request.query:
            response.body = pformat(response.body)
        self.logger.error(response)
        return response

    async def handle_not_found(self, request: web.BaseRequest):
        raise web.HTTPNotFound

    async def handle_error(self, e: Exception):
        self.logger.error(e, exc_info=True)
        return self.handler.internal_error(e)

    def run(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        routes = self.handler.bind_routes(self)
        loop.run_until_complete(self.create_app(loop, routes))
        self.logger.critical('LISTENING: %s:%d' % (self.host, self.port))
        self.logger.critical('ROUTES: %s' % pformat(self.handler.routes))
        self.is_ready.set()
        loop.run_forever()

    def close(self):
        self.terminate()