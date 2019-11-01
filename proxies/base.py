
from ..cli import set_logger
from multiprocessing import Process, Event
from aiohttp import web, web_exceptions
import itertools
import argparse
import asyncio
from .. import models


class Response:
    @staticmethod
    def json_200(response: dict):
        return web.json_response(response, status=200)

    @staticmethod
    def exception_500(ex: Exception):
        return web.json_response(dict(error=str(ex), type=type(ex).__name__), status=500)


class RouteHandler:
    routes = []

    def add_route(self, method, path):
        def decorator(f):
            self.routes += [(method, path, f)]
            return f
        return decorator

    def bind_routes(self, obj):
        return [web.route(method, path, getattr(obj, f.__name__)) for method, path, f in self.routes]


class BaseProxy(Process):
    handler = RouteHandler()

    def __init__(self, args: 'argparse.Namespace'):
        super().__init__()
        self.args = args
        self.queries = dict()
        self.model = getattr(models, self.args.model)(self.args)
        self.counter = itertools.count()
        self.logger = set_logger(self.__class__.__name__)
        self.is_ready = Event()

    async def default_handler(self, request: 'web.BaseRequest'):
        return Response.json_200({})

    @web.middleware
    async def middleware(self, request: 'web.BaseRequest', handler):
        try:
            self.logger.info('Recieved %s request for %s' % (request.method, request.path))
            self.logger.info('Processing with %s' % handler.__name__)
            return await handler(request)

        except web_exceptions.HTTPNotFound:
            self.logger.info('Error 404, falling back to %s' % self.default_handler.__name__)
            return await self.default_handler(request)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            return Response.exception_500(ex)

    def _run(self):
        loop = asyncio.get_event_loop()
        routes = self.handler.bind_routes(self)

        async def create_site():
            app = web.Application(middlewares=[self.middleware])
            app.add_routes(routes)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.args.proxy_host, self.args.proxy_port)
            await site.start()

        loop.run_until_complete(create_site())
        self.logger.info('proxy forwarding %s:%d to %s:%d' % (
            self.args.proxy_host, self.args.proxy_port,
            self.args.server_host, self.args.server_port))

        self.is_ready.set()
        loop.run_forever()

    def run(self):
        try:
            self._run()
        except Exception as ex:
            self.logger.error(ex, exc_info=True)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

