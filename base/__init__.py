from ..cli import set_logger
from multiprocessing import Process, Event
from aiohttp import web, web_exceptions
import asyncio


class Response:
    @staticmethod
    def json_200(response: dict):
        return web.json_response(response, status=200)

    @staticmethod
    def status_404():
        return web.json_response(status=404)

    @staticmethod
    def exception_500(ex: Exception):
        return web.json_response(dict(error=str(ex), type=type(ex).__name__), status=500)


class RouteHandler:
    def __init__(self):
        self.routes = []

    def add_route(self, method, path):
        def decorator(f):
            self.routes += [(method, path, f)]
            return f

        return decorator

    def bind_routes(self, obj):
        return [web.route(method, path, getattr(obj, f.__name__)) for method, path, f in self.routes]


class BaseServer(Process):
    handler = RouteHandler()

    def __init__(self, host: str = '127.0.0.1', port: int = 53001, **kwargs):
        super().__init__()
        self.logger = set_logger(self.__class__.__name__)
        self.host = host
        self.port = port
        self.is_ready = Event()

    async def default_handler(self, request: 'web.BaseRequest'):
        return Response.status_404()

    @web.middleware
    async def middleware(self, request: 'web.BaseRequest', handler):
        try:
            self.logger.info('%s request %s' % (request.method, request.path))
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
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            self.logger.critical('listening on  %s:%d' % (self.host, self.port))
            self.is_ready.set()

        loop.run_until_complete(create_site())
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
