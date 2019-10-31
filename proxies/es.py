from .base import BaseProxy
from aiohttp import web
from typing import Tuple, List, Any
from ..models.test import TestModel

from aiohttp import web, client
import aiohttp


class ESProxy(BaseProxy):
    routes = web.RouteTableDef()

    def __init__(self, host, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.model = TestModel(*args)
        self.requests = dict()
        self.counter = 0

    @handler.register(r'/train')
    async def train(self, request: 'web.BaseRequest'):
        data = await request.json()
        field, query, candidates = self.requests[data['qid']]
        selected = data['cid'] # candidate that was selected by user
        labels = [1 if i == selected else 0 for i in range(len(candidates))]
        self.model.train(query, candidates, labels=labels)

    @handler.register(r'/{index}/search')
    async def search(self, request: 'web.BaseRequest') -> dict:
        request_data = request.json()
        field, query = request.rel_url.query['q'].split(':')
        topk = 10
        url = request.rel_url.with_host(self.host).with_port(self.port).human_repr()
        async with aiohttp.request(request.method, url, data=request.json()) as resp:
            assert resp.status == 200
            data = await resp.json()
            candidates = self.get_candidates(resp, field)
            self.requests[self.counter] = (field, query, candidates)
            self.counter += 1
            ranks = self.model.rank(query, candidates)
            response_dict =  self.reorder(data, ranks)
            return response_dict

    def reorder(self, data, ranks: List[int]) -> dict:
        data['hits']['hits']  = [data['hits']['hits'][i] for i in ranks]
        return data

    def get_candidates(self, response: 'client.ClientResponse', field: str):
        data = await response.json()
        candidates = [hit['_source'][field] for hit in data['hits']['hits']]
        return candidates