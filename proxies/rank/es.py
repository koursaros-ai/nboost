from ..base import RouteHandler, Response
from .base import RankProxy
from typing import Tuple, List, Any

from aiohttp import web, client
import aiohttp


class ESRankProxy(RankProxy):
    handler = RouteHandler()
    search_path = '/{index}/_search'

    async def magnify(self, request):
        size = request.query['size'] if 'size' in request.query else 10
        size *= self.multiplier
        ext_url = (
            request
            .rel_url
            .with_host(self.ext_host)
            .with_port(self.ext_port)
            .human_repr()
        )
        return request.method, ext_url, request.content

    async def parse(self, request, client_response):
        data = await client_response.json()
        candidates = [hit['_source'][self.field] for hit in data['hits']['hits']]
        return request.query['q'], candidates

    async def reorder(self, client_response, ranks):
        data = await client_response.json()
        data['hits']['hits'] = [data['hits']['hits'][i] for i in ranks]
        return Response.json_200(data)

