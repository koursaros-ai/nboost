from ..base import BaseProxy, RouteHandler, Response
from aiohttp import web, client
from typing import List, Tuple, Any


class RankProxy(BaseProxy):
    handler = RouteHandler(BaseProxy.handler)
    search_path = '/search'
    train_path = '/train'

    def __init__(self, multiplier: int = 10, field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.field = field
        self.handler.add_route('*', self.search_path)(self.search)
        self.handler.add_route('*', self.train_path)(self.train)

    async def status(self, request):
        return Response.json_200(dict(res='Chillin'))

    async def train(self, request: 'web.BaseRequest') -> 'web.Response':
        qid = int(request.query['qid'])
        cid = int(request.query['cid'])

        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1
        self.model.train(query, candidates, labels)
        return Response.json_200({})

    async def search(self, request: 'web.BaseRequest') -> 'web.Response':
        topk, method, ext_url, data = await self.magnify(request)
        async with self.client_handler(method, ext_url, data) as client_response:
            self.logger.info(repr(client_response).split('\n')[0])
            query, candidates = await self.parse(request, client_response)
            ranks = await self.model.rank(query, candidates)
            response = await self.reorder(client_response, topk, ranks)
            qid = next(self.counter)
            self.queries[qid] = query, candidates
            response.headers['qid'] = str(qid)
            return response

    async def magnify(self, request: 'web.BaseRequest') -> Tuple[int, str, str, bytes]:
        """
        Magnify the size of the request by the multiplier
        :return topk, method, ext_url, data
        """
        raise NotImplementedError

    async def parse(
            self,
            request: 'web.BaseRequest',
            client_response: 'client.ClientResponse') -> Tuple[str, List[str]]:
        """
        Parse out the query and candidates
        :return: query, candidates
        """
        raise NotImplementedError

    async def reorder(self,
                      client_response: 'client.ClientResponse',
                      topk: int,
                      ranks: List[int]) -> 'web.Response':
        """
        Reorder the client response by the ranks from the model
        """
        raise NotImplementedError
