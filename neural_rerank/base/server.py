from ..cli import format_async_response, format_async_request, format_pyobj
from . import Base, Response, Handler
from multiprocessing import Process, Event
from aiohttp import web, web_exceptions
import asyncio


class BaseServer(Base, Process):
    handler = Handler(Base.handler)

    def __init__(self, host: str = '127.0.0.1', port: int = 53001, **kwargs):
        super().__init__()
        self.host = host
        self.port = port
        self.is_ready = Event()
        self.traffic = {}

    @handler.add_state()
    def is_ready(self) -> bool:
        return self.is_ready.is_set()

    @handler.add_state()
    def traffic(self):
        return self.traffic

    @handler.add_route('*', '/status')
    async def _status(self, request: web.BaseRequest):
        return Response.JSON_OK(self.handler.get_states(self))

    @web.middleware
    async def middleware(self, request: web.BaseRequest, handler) -> web.Response:
        try:
            self.traffic.setdefault(request.path, 0)
            self.traffic[request.path] += 1
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

        if 'pretty' in request.query:
            response.body = format_pyobj(response.body)

        return response

    async def not_found_handler(self, request: web.BaseRequest):
        raise web_exceptions.HTTPNotFound

    def _run(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        routes = self.handler.get_routes(self)

        async def create_site():
            app = web.Application(middlewares=[self.middleware])
            app.add_routes(routes)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            self.logger.critical('LISTENING: %s:%d' % (self.host, self.port))
            self.logger.critical('ROUTES: %s' % self.handler.routes)
            self.is_ready.set()

        loop.run_until_complete(create_site())
        loop.run_forever()

    def run(self):
        try:
            self._run()
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
