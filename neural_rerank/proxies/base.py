from ..base import BaseServer, Response, Handler
from ..clients import BaseClient
from ..models import BaseModel
from ..cli import format_pyobj
from aiohttp import web
import itertools


class BaseProxy(BaseClient, BaseModel, BaseServer):
    requires = BaseClient, BaseModel, BaseServer
    handler = Handler(BaseClient.handler, BaseModel.handler, BaseServer.handler)
    _search_path = '/search'
    _train_path = '/train'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries = dict()
        self.counter = itertools.count()
        self.handler.add_route('*', self._search_path)(self._search)
        self.handler.add_route('*', self._train_path)(self._train)

    @handler.add_state()
    def queries(self):
        return list(self.queries)

    @handler.add_state()
    def search_path(self):
        return self._search_path

    @handler.add_state()
    def train_path(self):
        return self._train_path

    async def _train(self, request: web.BaseRequest) -> web.Response:
        req = await request.json()

        query, candidates = self.queries[req['qid']]
        labels = [0] * len(candidates)
        labels[req['cid']] = 1

        self.logger.info('TRAIN: %s' % query)
        self.logger.debug('candidates: %s\nlabels:%s' % (
            format_pyobj(candidates), format_pyobj(labels)))

        await self.train(query, candidates, labels)
        return Response.NO_CONTENT()

    async def _search(self, request: web.BaseRequest) -> web.Response:
        topk, method, ext_url, data = await self.magnify(request)
        async with self.client_handler(method, ext_url, data) as client_response:
            self.logger.info('RECV: ' + repr(client_response).split('\n')[0])
            query, candidates = await self.parse(request, client_response)
            self.logger.info('RANK: %s' % query)
            self.logger.debug('candidates: %s' % format_pyobj(candidates))
            ranks = await self.rank(query, candidates)
            response = await self.format(client_response, topk, ranks)
            qid = next(self.counter)
            self.queries[qid] = query, candidates
            response.headers['qid'] = str(qid)
            return response

