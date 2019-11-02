from ..base import BaseProxy, RouteHandler, Response
from aiohttp import web, client
from typing import List, Tuple, Any


class RankProxy(BaseProxy):
    handler = RouteHandler()
    search_path = '/search'
    train_path = '/train'

    def __init__(self, multiplier: int = 10, field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.field = field

    async def status(self, request):
        return Response.json_200(dict(res='Chillin'))

    @handler.add_route('*', train_path)
    async def train(self, request: 'web.BaseRequest') -> 'web.Response':
        qid = int(request.query['qid'])
        cid = int(request.query['cid'])

        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1
        self.model.train(query, candidates, labels)
        return Response.json_200({})

    @handler.add_route('*', search_path)
    async def search(self, request: 'web.BaseRequest') -> 'web.Response':
        method, ext_url, data = await self.magnify(request)
        client_response = await self.client_handler(method, ext_url, data)
        query, candidates = await self.parse(request, client_response)
        ranks = await self.model.rank(query, candidates)
        response = await self.reorder(client_response, ranks)

        qid = next(self.counter)
        self.queries[qid] = query, candidates
        response.headers['qid'] = qid
        return response

    async def magnify(self, request: 'web.BaseRequest') -> Tuple[str, str, bytes]:
        """ :return method, ext_url, data"""
        raise NotImplementedError

    async def parse(
            self,
            request: 'web.BaseRequest',
            client_response: 'client.ClientResponse') -> Tuple[str, List[str]]:
        """
        :return: query, candidates
        """
        raise NotImplementedError

    async def reorder(self,
                      client_response: 'client.ClientResponse',
                      ranks: List[int]) -> 'web.Response':
        raise NotImplementedError
