from pprint import pformat
from ..base import *
import json as JSON
import gzip


class ElasticsearchError(Exception):
    pass


class ESCodex(BaseCodex):
    SEARCH = {'/{index}/_search': ['GET']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.field:
            self.logger.error(
                'Please set --field which you would like to rank on')
            raise NotImplementedError

    def topk(self, req):
        # try to get the nested size and otherwise default to 10
        try:
            # check request parameters
            return Topk(req.params['size'])
        except KeyError:
            pass

        # if not in params and no req body then return default
        if req.body:
            body = JSON.loads(req.body)
        else:
            return Topk(10)

        try:
            return Topk(body['size'])
        except KeyError:
            pass

        try:
            return Topk(body['collapse']['inner_hits']['size'])
        except KeyError:
            pass

        # if size is not found
        return Topk(10)

    def magnify(self, req, topk):
        mtopk = topk * self.multiplier
        topk_is_set = False
        body = req.body
        req.headers.pop('Content-Length', None)

        if body:
            body = JSON.loads(req.body)

            if 'size' in body:
                body['size'] = mtopk
                topk_is_set = True

            try:
                # if it's in inner hits set to topk
                _ = body['collapse']['inner_hits']['size']
                body['collapse']['inner_hits']['size'] = mtopk
                topk_is_set = True
            except KeyError:
                pass

            body = JSON.dumps(body).encode()

        if not topk_is_set:
            req.params['size'] = mtopk

        return Request(req.method, req.path, req.headers, req.params, body)

    def parse(self, req, res):

        if res.status >= 400:
            raise ElasticsearchError(res.body)

        if 'q' in req.params:
            query = req.params['q'].split(':')[-1]
        elif req.body:
            body = JSON.loads(req.body)
            try:
                query = body['query']['match'][self.field]
                if isinstance(query, dict):
                    query = query['query']
            except KeyError:
                raise ValueError('Missing query')

        else:
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
