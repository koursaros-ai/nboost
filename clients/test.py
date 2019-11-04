
from ..base import Response
from .base import BaseClient


class TestClient(BaseClient):
    async def magnify(self, request):
        """ receives and sends topk from query params """
        topk = int(request.query['topk']) if 'topk' in request.query else 10
        ext_url = self.ext_url(request)
        params = dict(ext_url.query)
        params['topk'] = topk * self.multiplier
        ext_url = ext_url.with_query(params)
        return topk, request.method, ext_url, await request.read()

    async def parse(self, request, client_response):
        """ gets query from q param and candidates from body """
        query = request.query['q']
        candidates = await client_response.json()
        return query, candidates

    async def format(self, client_response, reranked):
        return Response.JSON_OK(reranked)
