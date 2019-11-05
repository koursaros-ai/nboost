
from ..base import Response
from .base import BaseClient
from .helpers import parse_json_request_qid_cid


class TestClient(BaseClient):
    async def magnify_request(self, request):
        """ receives and sends topk from query params """
        topk = int(request.query['topk']) if 'topk' in request.query else 10
        ext_url = self.ext_url(request)
        params = dict(ext_url.query)
        params['topk'] = topk * self.multiplier
        ext_url = ext_url.with_query(params)
        return topk, request.method, ext_url, await request.read()

    async def parse_query_candidates(self, request, client_response):
        """ gets query from q param and candidates from body """
        query = request.query['q']
        candidates = await client_response.json()
        return query, candidates

    async def format_response(self, client_response, topk, ranks, qid):
        candidates = await client_response.json()
        reranked = [candidates[i] for i in ranks[:topk]]
        response = Response.JSON_OK(reranked)
        response.headers['qid'] = str(qid)
        return response

    async def parse_qid_cid(self, request):
        return await parse_json_request_qid_cid(request)
