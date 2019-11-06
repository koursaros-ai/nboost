from ..base import BaseLogger, pfmt, pfmt_obj
from pprint import pformat
from multiprocessing import Process, Event
# import multiprocessing as mp
from aiohttp import web_exceptions, web_routedef, web
from typing import List, Callable
from .handler import ServerHandler
import asyncio
import time


def running_avg(avg: float, new: float, n: int):
    return (avg * n + new) / n


# ctx = mp.get_context('spawn')


class BaseServer(BaseLogger, Process):
    handler = ServerHandler()

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 read_bytes: int = 2048,
                 status_path: str = '/status',
                 status_method: str = '*',
                 **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.read_bytes = read_bytes
        self.is_ready = Event()
        self.handler.add_route(status_method, status_path)(self.status)

    @handler.add_state
    def host(self):
        return self.host

    @handler.add_state
    def port(self):
        return self.port

    @handler.add_state
    def read_bytes(self):
        return self.read_bytes

    @handler.add_state
    def is_ready(self):
        return self.is_ready.is_set()

    @property
    def state(self):
        return {self.__class__.__name__: self.handler.bind_states(self)}

    async def status(self, request: web.BaseRequest):
        return self.handler.json_ok(self.state)

    @web.middleware
    async def middleware(self,
                         request: web.BaseRequest,
                         handler: Callable) -> web.Response:

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

    async def handle_not_found(self, request: web.BaseRequest):
        raise web.HTTPNotFound

    async def handle_error(self, e: Exception):
        return self.handler.internal_error(e)

    async def create_app(self,
                         loop: asyncio.AbstractEventLoop,
                         routes: List[web_routedef.RouteDef]) -> None:
        app = web.Application(middlewares=[self.middleware])
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

    def run(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        routes = self.handler.bind_routes(self)
        loop.run_until_complete(self.create_app(loop, routes))
        self.logger.critical('LISTENING: %s:%d' % (self.host, self.port))
        self.logger.info('\nROUTES:\n%s' % pformat(self.handler.routes, width=1))
        self.is_ready.set()
        loop.run_forever()

    def close(self):
        self.terminate()
        self.join()
