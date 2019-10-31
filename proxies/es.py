from .base import BaseProxy
from typing import Tuple, List, Any

from aiohttp import web, client
import aiohttp


class ESProxy(BaseProxy):
    def __init__(self, host, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port

    def query(self, request: 'web.BaseRequest') -> Tuple[Any, str, List[str], int]:
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
        pass

    def get_candidates(self, response: 'client.ClientResponse', field: str):
        candidates = [hit['_source'][field] for hit in data['hits']['hits']]
        return candidates