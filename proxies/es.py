from .base import BaseProxy
from typing import Tuple, List, Any

from aiohttp import web, client
import aiohttp


class ESProxy(BaseProxy):
    routes = web.RouteTableDef()

    def __init__(self, host, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port

    @routes.get('/search')
    async def search(self, request: 'web.BaseRequest'):
        pass

    @routes.post('/train')
    async def train(self, request: 'web.BaseRequest'):
        pass

    async def query(self, request: 'web.BaseRequest') -> Tuple[Any, str, List[str], int]:
        request_data = request.json()
        field, query = request.rel_url.query['q'].split(':')
        topk = 10
        url = request.rel_url.with_host(self.host).with_port(self.port).human_repr()
        async with aiohttp.request(request.method, url, data=request.json()) as resp:
            assert resp.status == 200
            data = await resp.json()
            candidates = self.get_candidates(resp, field)
            return (resp, query, candidates, topk)

    def reorder(self, response: 'client.ClientResponse', ranks: List[int]) -> dict:
        assert response.status == 200
        data = await response.json()
        data['hits']['hits']  = [data['hits']['hits'][i] for i in ranks]
        return data

    def get_candidates(self, response: 'client.ClientResponse', field: str):
        data = await response.json()
        candidates = [hit['_source'][field] for hit in data['hits']['hits']]
        return candidates