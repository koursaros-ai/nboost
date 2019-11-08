from .base import BaseCodex
import json as JSON
from ..base.types import *
from pprint import pformat
import gzip


def _finditem(obj, key):
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = _finditem(v, key)
            if item is not None:
                return item


class ESCodex(BaseCodex):
    DEFAULT_TOPK = 10
    SEARCH_PATH = '/{index}/_search'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.field:
            self.logger.error('Please set --field which you would like to rank on')
            raise NotImplementedError

    def get_topk(self, req: Request) -> int:
        return int(req.params['size'] if 'size' in req.params else self.DEFAULT_TOPK)

    def magnify(self, req):
        params = dict(req.params)
        params['size'] = self.get_topk(req) * self.multiplier
        return Request(req.method, req.path, req.headers, params, req.body)

    def parse(self, req, res):
        if 'q' in req.params:
            query = req.params['q']
        else:
            body = JSON.loads(req.body)
            query = _finditem(body['query'], 'query')

        hits = JSON.loads(res.body)['hits'].get('hits', None)
        if not hits:
            raise ValueError('No hits for req: %s' % query)

        choices = [hit['_source'][self.field].encode() for hit in hits]

        return Query(query), Choices(choices)

    def pack(self, req, res, query, choices, ranks, qid, cids):
        body = JSON.loads(res.body)
        for choice, cid, hit in zip(choices, cids, body['hits']['hits']):
            hit['qid'] = qid
            hit['cid'] = cid

        body['hits']['hits'] = [body['hits']['hits'][i] for i in ranks[:self.get_topk(req)]]
        res.headers.pop('Content-Length', None)
        body = JSON.dumps(body).encode()
        if res.headers.get('Content-Encoding', None) == 'gzip':
            body = gzip.compress(body)
        return Response(res.headers, body, 200)

    def pluck(self, req):
        body = JSON.loads(req.body)
        if 'qid' in body:
            qid = body['qid']
        elif 'qid' in req.params:
            qid = req.params['qid']
        else:
            raise ValueError('qid not found')

        if 'cid' in body:
            cids = [Cid(body['cid'])]
        elif 'cid' in req.params:
            cids = [Cid(req.params['cid'])]
        elif 'cids' in body:
            cids = [Cid(cid) for cid in body['cids']]
        elif 'cids' in req.params:
            cids = [Cid(cid) for cid in req.params['cids']]
        else:
            raise ValueError('cid not found')

        return Qid(qid), cids

    def ack(self, qid, cids):
        return Response({}, JSON.dumps(dict(qid=qid, cid=cids)).encode(), 200)

    def catch(self, e):
        body = JSON.dumps(dict(error=str(e), type=type(e).__name__))
        return Response({}, body, 500)

    def pulse(self, state):
        return Response({}, pformat(state), 200)
