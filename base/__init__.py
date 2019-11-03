from ..cli import set_logger, format_async_response, format_async_request
from multiprocessing import Process, Event
from aiohttp import web, web_exceptions
import copy
import asyncio


class Response:
    PLAIN_OK = lambda x: web.Response(body=x, status=200)
    JSON_OK = lambda x: web.json_response(x, status=200)
    NO_CONTENT = lambda: web.Response(status=204)
    INTERNAL_ERROR = lambda x: web.json_response(
        dict(error=str(x), type=type(x).__name__), status=500)


class RouteHandler:
    def __init__(self, rh: 'RouteHandler' = None):
        self.routes = copy.deepcopy(rh.routes) if rh else []

    def add_route(self, method, path):
        def decorator(f):
            self.routes += [(method, path, f)]
            return f

        return decorator

    def bind_routes(self, obj):
        return [web.route(method, path, getattr(obj, f.__name__)) for method, path, f in self.routes]


class BaseProcess(Process):
    def __new__(cls, verbose=False, **kwargs):
        cls.logger = set_logger(cls.__name__, verbose=verbose)
        cls.logger.info('\nINIT: %s%s' % (cls.__name__, cls._format_kwargs(kwargs)))
        return super().__new__(cls)

    @classmethod
    def _format_kwargs(cls, kwargs):
        return ''.join([cls._format_kwarg(k, v) for k, v in kwargs.items()])

    @staticmethod
    def _format_kwarg(k, v):
        switch = k[:14], ' ' * (15 - len(k)), v, v.__class__.__name__
        return '\n\t--%s%s%s (%s)' % switch

    def _run(self):
        raise NotImplementedError

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


class BaseServer(BaseProcess):
    handler = RouteHandler()

    def __init__(self, host: str = '127.0.0.1', port: int = 53001, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.is_ready = Event()

    async def not_found_handler(self, request: 'web.BaseRequest'):
        raise web_exceptions.HTTPNotFound

    @web.middleware
    async def middleware(self, request: 'web.BaseRequest', handler) -> 'web.Response':
        try:
            self.logger.info('RECV: %s' % request)
            self.logger.debug(await format_async_request(request))
            response = await handler(request)

        except web_exceptions.HTTPNotFound:
            response = await self.not_found_handler(request)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            response = Response.INTERNAL_ERROR(ex)

        self.logger.info('SEND: %s' % response)
        self.logger.debug(await format_async_response(response))
        return response

    def _run(self):
        loop = asyncio.get_event_loop()
        routes = self.handler.bind_routes(self)

        async def create_site():
            app = web.Application(middlewares=[self.middleware])
            app.add_routes(routes)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            self.logger.critical('listening on  %s:%d' % (self.host, self.port))
            self.is_ready.set()

        loop.run_until_complete(create_site())
        loop.run_forever()
