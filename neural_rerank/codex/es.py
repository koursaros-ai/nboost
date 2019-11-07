from .base import BaseCodex
import json as JSON
from ..base.types import *


class ESCodex(BaseCodex):
    DEFAULT_TOPK = 10
    SEARCH_PATH = '/{index}/_search'

    def get_topk(self, req: Request) -> Topk:
        return Topk(req.params['size'] if 'size' in req.params else self.DEFAULT_TOPK)

    def magnify(self, req):
        params = dict(req.params)
        params['size'] = self.get_topk(req) * self.multiplier
        return Request(req.method, req.path, req.headers, params, req.body)

    def parse(self, req, res):
        query = Query(req.params['q'] if 'q' in req.params else '')
        hits = JSON.loads(res.body)['hits']['hits']
        choices = [Choice(
            int(hit['_id']), hit['_source'][self.field]
        ) for hit in hits]

        return query, choices

    def pack(self, req, res, query, choices, ranks):
        body = JSON.loads(res.body)
        for choice, hit in zip(choices, body['hits']['hits']):
            hit['cid'] = choice.id
        body['hits']['hits'] = [body['hits']['hits'][i] for i in ranks[:self.get_topk(req)]]
        res.headers.pop('Content-Length', None)
        return Response(res.headers, JSON.dumps(body).encode(), 200)

    def pluck(self, req):
        body = JSON.loads(req.body)
        cid = body['cid'] if 'cid' in body else req.params['cid'] if 'cid' in req.params else None

        if cid is None:
            raise ValueError('cid not found')

        return Cid(cid)

    def ack(self, cid):
        return Response({}, JSON.dumps(dict(cid=cid)).encode(), 200)

    def catch(self, e):
        body = JSON.dumps(dict(error=str(e), type=type(e).__name__))
        return Response({}, body, 500)

    def pulse(self, state):
        return Response({}, JSON.dumps(state).encode(), 200)
