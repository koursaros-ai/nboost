
from ..cli import set_logger
from multiprocessing import Process
from aiohttp import web
import itertools
import functools
import argparse
import asyncio
from .. import models, clients


async def route_handler(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        logger = set_logger(f.__name__)
        try:
            logger.info('new %s request' % f.__name__)
            ret = f(*args, **kwargs)
            return web.json_response(ret, status=200)
        except Exception as ex:
            logger.error('Error on %s request' % f.__name__, exc_info=True)
            return web.json_response(dict(error=str(ex), type=type(ex).__name__), status=500)

    return decorator


class BaseProxy(Process):
    def __init__(self, args: 'argparse.Namespace'):
        super().__init__()
        self.args = args
        self.queries = dict()
        self.model = models[self.args.model](self.args)
        self.client = clients[self.args.client](self.args)
        self.counter = itertools.count()
        self.loop = asyncio.get_event_loop()
        self.logger = set_logger(self.__class__.__name__)
        self.app = self.create_app()
        self.runner = self.create_runner()
        self.site = self.create_site()

    def create_app(self):
        app = web.Application()
        app.add_routes([
            web.get('/status', self._status),
            web.get('/query', self._query),
            web.post('/train', self._train),
        ])
        return app

    def create_runner(self):
        return web.AppRunner(self.app)

    def create_site(self):
        return web.TCPSite(self.runner, self.args.proxy_host, self.args.proxy_port)

    async def status(self) -> dict:
        raise NotImplementedError

    async def query(self, request: 'web.BaseRequest') -> dict:
        raise NotImplementedError

    async def train(self, request: 'web.BaseRequest') -> dict:
        raise NotImplementedError

    def _status(self):
        return route_handler(self.status)

    def _query(self):
        return route_handler(self.query)

    def _train(self):
        return route_handler(self.train)

    def _run(self):
        self.loop.run_until_complete(self.runner.setup())
        self.loop.run_until_complete(self.site.start())

        self.logger.info('proxy forwarding %s:%d to %s:%d' % (
            self.args.proxy_host, self.args.proxy_port,
            self.args.server_host, self.args.server_port))

    def stop(self):
        self.loop.run_until_complete(self.site.stop())
        self.join()

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

