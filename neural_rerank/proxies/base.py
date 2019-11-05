from ..base import *
from .handler import ProxyHandler
from ..clients import BaseClient
from ..models import BaseModel
from multiprocessing import Process, Event
from typing import List
import asyncio
import aiohttp
from aiohttp import web_exceptions, web_routedef
import itertools


class BaseProxy(Base, Process):
    handler = ProxyHandler()

    def __init__(self,
                 client: BaseClient = BaseClient,
                 model: BaseModel = BaseModel,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 read_bytes: int = 2048,
                 status_path: str = '/status',
                 search_path: str = '/search',
                 train_path: str = '/train', **kwargs):
        super().__init__(**kwargs)
        self.client = client
        self.model = model
        self._host = host
        self._port = port
        self._read_bytes = read_bytes
        self._queries = {}
        self._is_ready = Event()
        self.counter = itertools.count()
        self.handler.add_route('*', status_path)(self.status)
        self.handler.add_route('*', search_path)(self.search)
        self.handler.add_route('*', train_path)(self.train)

    @property
    def state(self):
        return {
            self.__name__: self.handler.bind_states(self),
            self.model.__name__: self.model.handler.bind_states(self.model),
            self.client.__name__: self.client.handler.bind_states(self.client)
        }

    async def status(self, request: web.BaseRequest):
        return self.handler.json_ok(self.state)

    @handler.add_state
    def host(self):
        return self._host

    @handler.add_state
    def port(self):
        return self._port

    @handler.add_state
    def read_bytes(self):
        return self._read_bytes

    @handler.add_state
    def backlog(self):
        return len(self._queries)

    @web.middleware
    async def middleware(self, request: web.BaseRequest, handler: Callable) -> web.Response:
        try:
            response = await handler(request)
        except web_exceptions.HTTPNotFound:
            response = await self.handle_not_found(request)
        except Exception as ex:
            response = self.handle_error(ex)

        if 'pretty' in request.query:
            response.body = pformat(response.body)

        return response

    async def pipe(self, reader, writer):
        try:
            while not reader.at_eof():
                writer.write(await reader.read(self._read_bytes))
        finally:
            writer.close()

    async def handle_not_found(self, request: web.BaseRequest):
        self.handler.redirect(request.url)
        # try:
        #     remote_reader, remote_writer = await asyncio.open_connection(
        #         '127.0.0.1', 9200)
        #     pipe1 = self.pipe(local_reader, remote_writer)
        #     pipe2 = self.pipe(remote_reader, local_writer)
        #     await asyncio.gather(pipe1, pipe2)
        # finally:
        #     local_writer.close()

    async def handle_error(self, e: Exception):
        self.logger.error(e, exc_info=True)
        return self.handler.internal_error(e)

    async def create_app(self,
                         loop: asyncio.AbstractEventLoop,
                         routes: List[web_routedef.RouteDef]) -> None:
        app = web.Application(middlewares=[self.middleware])
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self._host, self._port)
        await site.start()

    async def train(self, request: web.BaseRequest) -> web.Response:
        qid, cid = await self.client.parse_qid_cid(request)
        query, candidates = self._queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1

        self.logger.info('TRAIN: %s' % query)
        self.logger.debug('candidates: %s\nlabels:%s' % (pformat(candidates), pformat(labels)))

        await self.model.train(query, candidates, labels)
        return self.handler.no_content()

    async def search(self, request: web.BaseRequest) -> web.Response:
        topk, method, ext_url, data = await self.client.magnify_request(request)
        self.logger.info('PROXY: <Request %s %s >' % (method, ext_url))
        self.logger.debug(pfmt_obj(data))

        async with aiohttp.request(method, ext_url, data=data) as client_response:
            self.logger.info('RECV: ' + repr(client_response).split('\n')[0])
            query, candidates = await self.client.parse_query_candidates(request, client_response)

            self.logger.info('RANK: %s' % query)
            self.logger.debug('candidates: %s' % pformat(candidates))
            ranks = await self.model.rank(query, candidates)
            qid = next(self.counter)
            self._queries[qid] = query, candidates
            response = await self.client.format_response(client_response, topk, ranks, qid)

            return response

    def run(self):
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            routes = self.handler.bind_routes(self)
            loop.run_until_complete(self.create_app(loop, routes))
            self.logger.critical('LISTENING: %s:%d' % (self._host, self._port))
            self.logger.critical('ROUTES: %s' % pformat(self.handler.routes))
            self._is_ready.set()
            loop.run_forever()
        except Exception as ex:
            self.logger.error(ex, exc_info=True)

    def close(self):
        self.terminate()


