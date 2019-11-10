from .base import BaseCodex
from ..base.types import *
from pprint import pformat
import json as JSON
import gzip


class ElasticsearchError(Exception):
    pass


class ESCodex(BaseCodex):
    DEFAULT_TOPK = 10
    SEARCH = {'/{index}/_search': ['GET']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.field:
            self.logger.error(
                'Please set --field which you would like to rank on')
            raise NotImplementedError

    def finddict(self, obj: dict, key: str):
        """recursively find the mutable dictionary containing a key (if any)"""
        if key in obj:
            return obj
        for k, v in obj.items():
            if isinstance(v, dict):
                return self.finddict(v, key)

    def finditem(self, obj: dict, key: str):
        return self.finddict(obj, key).get(key, None)

    def topk(self, req):
        topk = req.params.get('size', None)
        if topk is None and req.body:
            body = JSON.loads(req.body)
            topk = self.finditem(body, 'size')

        if topk is None:
            topk = self.DEFAULT_TOPK

        return Topk(topk)

    def magnify(self, req, topk):
        if req.body:
            body = JSON.loads(req.body)
            size = self.finddict(body, 'size')
            size['size'] = topk * self.multiplier
            body = JSON.dumps(body).encode()
            req.headers.pop('Content-Length', None)
            req = Request(req.method, req.path, req.headers, req.params, body)
        elif 'size' in req.params:
            req.params['size'] = topk * self.multiplier
        else:
            raise ValueError('Could not find "size" ')

        return req

    def parse(self, req, res):

        if res.status >= 400:
            raise ElasticsearchError(res.body)

        if 'q' in req.params:
            query = req.params['q'].split(':')[-1]
        else:
            body = JSON.loads(req.body)
            query = self.finditem(body['query'], 'query')

        if not query:
            raise ValueError('Missing query')

        hits = JSON.loads(res.body).get('hits', None)
        if not hits:
            choices = []
        else:
            choices = [hit['_source'][self.field].encode() for hit in hits['hits']]

        return Query(query, 'utf8'), Choices(choices)

    def pack(self, topk, res, query, choices, ranks, qid, cids):
        body = JSON.loads(res.body)
        body['qid'] = qid
        for choice, cid, hit in zip(choices, cids, body['hits']['hits']):
            hit['qid'] = qid
            hit['cid'] = cid

        body['hits']['hits'] = [body['hits']['hits'][i] for i in ranks[:topk]]
        res.headers.pop('Content-Length', None)
        body = JSON.dumps(body).encode()
        if res.headers.get('Content-Encoding', None) == 'gzip':
            body = gzip.compress(body)
        return Response(res.headers, body, 200)

    def pluck(self, req):
        body = JSON.loads(req.body) if req.body else {}
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
        body = JSON.dumps(dict(error=repr(e), type=type(e).__name__))
        return Response({}, body, 500)

    def pulse(self, state):
        return Response({}, pformat(state), 200)
