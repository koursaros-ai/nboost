
from ..cli import set_logger
from multiprocessing import Process, Event
from aiohttp import web
import itertools
import functools
import argparse
import asyncio
from .. import models


class RouteHandler:
    routes = dict()

    def register(self, f):
        @functools.wraps(f)
        async def decorator(*args, **kwargs):
            logger = set_logger(f.__name__)
            try:
                logger.info('new %s request' % f.__name__)
                ret = await f(*args, **kwargs)
                return web.json_response(ret, status=200)
            except Exception as ex:
                logger.error('Error on %s request' % f.__name__, exc_info=True)
                return web.json_response(dict(error=str(ex), type=type(ex).__name__), status=500)

        self.routes['/%s' % f.__name__] = decorator


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

    @handler.register
    async def default_route(self, request):
        pass

    async def request_handler(self, request: 'web.BaseRequest'):
        f = self.handler.routes.get(request.path, self.default_route)
        return f(request)

    def _run(self):
        loop = asyncio.get_event_loop()

        async def create_site():
            app = web.Application()
            app.router.add_route('*', '/{path:.*}', self.request_handler)
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

