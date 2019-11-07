from ..base import *
from ..server import BaseServer, ServerHandler
from ..clients import BaseClient
from ..model import BaseModel
import aiohttp
from aiohttp import web
import itertools
from enum import Enum


class Route(Enum):
    SEARCH = 0
    TRAIN = 1
    STATUS = 2
    NOT_FOUND = 3
    ERROR = 4


class BaseProxy(BaseServer):
    handler = ServerHandler(BaseServer.handler)

    def __init__(self,
                 client: BaseClient = BaseClient,
                 model: BaseModel = BaseModel,
                 **kwargs):
        super().__init__(status_method=client.search_method, status_path=client.status_path, **kwargs)
        self.client = client
        self.model = model
        self.queries = {}
        self.counter = itertools.count()
        self.handler.add_route(self.client.search_method, self.client.search_path)(self.search)
        self.handler.add_route(self.client.train_method, self.client.train_path)(self.train)
        self.handler.add_route(self.client.train_method, self.client.bulk_train_path)(self.bulk_train)

    @property
    def state(self):
        return {}

    async def handle_not_found(self, request):
        # self.handler.redirect(self.client.ext_url(request))
        async with aiohttp.ClientSession() as session:
            headers = dict(request.headers)
            headers['Content-Type'] = 'application/json'
            path = request.url.with_host(self.client.ext_host).with_port(self.client.ext_port).human_repr()
            async with getattr(session, request.method.lower())(
                    path,
                    headers=headers,
                    data=request.content) as resp:
                return aiohttp.web.Response(status=resp.status,
                                            headers=resp.headers,
                                            body=await resp.content.read())

    async def train(self, request: web.BaseRequest) -> web.Response:
        qid, cid = await self.client.parse_qid_cid(request)
        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1

        self.logger.info('TRAIN: %s' % query)
        self.logger.debug('candidates: %s\nlabels:%s' % (pformat(candidates), pformat(labels)))

        await self.model.train(query, candidates, labels)
        return self.handler.no_content()

    async def bulk_train(self, request: web.BaseRequest) -> web.Response:
        examples = await request.json()
        await self.model.train(examples['query'], examples['candidates'], examples['labels'])
        return self.handler.no_content()

    async def search(self, request: web.BaseRequest) -> web.Response:
        topk, method, ext_url, data = await self.client.magnify_request(request)
        headers = dict(request.headers)
        headers['Content-Type'] = 'application/json'
        self.logger.info('PROXY: <Request %s %s >' % (method, ext_url))
        self.logger.debug(pfmt_obj(data))

        async with aiohttp.request(method, ext_url, data=data,headers=headers) as client_response:
            self.logger.info('RECV: ' + repr(client_response).split('\n')[0])
            query, candidates = await self.client.parse_query_candidates(request, client_response)

            self.logger.info('RANK: %s' % query)
            self.logger.debug('candidates: %s' % pformat(candidates))
            ranks = await self.model.rank(query, candidates)
            qid = next(self.counter)
            self.queries[qid] = query, candidates
            response = await self.client.format_response(client_response, topk, ranks, qid)

            return response

    def run(self):
        self.model.post_start()
        super().run()
