from termcolor import colored
import itertools
import functools
import asyncio
from aiohttp import web
from ..clients import clients
from ..models import models
from ..cli import set_logger

STATUS = {
    200: lambda x: web.json_response(x, status=200),
    500: lambda x: web.json_response(dict(error=str(x), type=type(x).__name__), status=500)
}


async def route_handler(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        logger = set_logger(f.__name__)
        try:
            logger.info('new %s request' % f.__name__)
            return STATUS[200](f(*args, **kwargs))
        except Exception as ex:
            logger.error('Error on %s request' % f.__name__, exc_info=True)
            return STATUS[500](ex)

    return decorator


class BaseProxy:
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.queries = dict()
        self.model = getattr(models, self.args.model)(self.args)
        self.client = getattr(clients, self.args.client)(self.args)
        self.counter = itertools.count()
        self.loop = asyncio.get_event_loop()

    async def status(self):
        pass

    async def query(self):
        pass

    async def train(self, request):
        pass

    @property
    def _status(self):
        return route_handler(self.status)

    @property
    def _query(self):
        return route_handler(self.query)

    @property
    def _train(self):
        return route_handler(self.train)

    async def main(self):
        app = web.Application()
        app.add_routes([
            web.get('/status', self.status),
            web.get('/query', self.query),
            web.post('/train', self.train),
        ])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.args.proxy_host, self.args.proxy_port)
        await site.start()

    def run(self):
        self.loop.run_until_complete(self.main())
        self.logger.info('proxy forwarding %s:%d to %s:%d' % (
            self.args.proxy_host, self.args.proxy_port,
            self.args.server_host, self.args.server_port))

    def stop(self):
        pass