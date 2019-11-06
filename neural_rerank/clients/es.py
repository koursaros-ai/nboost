from .base import BaseClient
from .helpers import parse_json_request_qid_cid
import json

DEFAULT_TOPK = 10


class ESClient(BaseClient):
    search_path = '/{index}/_search'

    async def magnify_request(self, request):
        topk = int(request.query['size']) if 'size' in request.query else DEFAULT_TOPK
        ext_url = self.ext_url(request)
        params = dict(ext_url.query)
        params['size'] = topk * self.multiplier
        ext_url = ext_url.with_query(params)
        return topk, request.method, ext_url, await request.read()

    async def parse_query_candidates(self, request, client_response):
        query = request.query['q']
        hits = (await client_response.json())['hits']['hits']
        candidates = [hit['_source'][self.field] for hit in hits]
        return query, candidates

    async def format_response(self, client_response, topk, ranks, qid):
        res = await client_response.json()
        res['hits']['hits'] = [res['hits']['hits'][i] for i in ranks[:topk]]
        res['qid'] = qid
        response = self.handler.json_ok(res)
        response.headers['qid'] = str(qid)
        return response

    async def parse_qid_cid(self, request):
        return await parse_json_request_qid_cid(request)
