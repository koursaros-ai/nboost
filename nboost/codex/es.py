from pprint import pformat
from ..base import *
import json as JSON
from typing import Tuple, List
import gzip


class ElasticsearchError(Exception):
    pass


class ESCodex(BaseCodex):
    SEARCH = (rb'/.*/_search', [b'GET'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.field:
            self.logger.error(
                'Please set --field which you would like to rank on')
            raise NotImplementedError

    def topk(self, req: Request) -> Topk:
        # try to get the nested size and otherwise default to 10
        try:
            # check request parameters
            return Topk(req.params[b'size'])
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

    def magnify(self, req: Request, topk: Topk) -> None:
        mtopk = topk * self.multiplier
        topk_is_set = False
        body = req.body

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

            req.body = JSON.dumps(body).encode()

        if not topk_is_set:
            req.params[b'size'] = str(mtopk).encode()

    def parse(self, req: Request, res: Response) -> Tuple[Query, List[Choice]]:
        if res.status >= 400:
            raise ElasticsearchError(res.body)

        if b'q' in req.params:
            query = req.params[b'q'].split(b':')[-1]
        elif req.body:
            body = JSON.loads(req.body)
            try:
                query = body['query']['match'][self.field]
                if isinstance(query, dict):
                    query = query['query']
                query = query.encode()
            except KeyError:
                raise ValueError('Missing query')

        else:
            raise ValueError('Missing query')

        hits = JSON.loads(res.body).get('hits', [])
        choices = []
        for hit in hits.get('hits', []):
            choices += [Choice(
                hit['_source'][self.field].encode(), ident=hit['_id']
            )]

        return Query(query), choices

    def pack(self,
             topk: Topk,
             res: Response,
             query: Query,
             choices: List[Choice]) -> None:
        body = JSON.loads(res.body)
        body['_nboost'] = query.ident.decode()
        body['hits']['hits'] = [body['hits']['hits'][c.rank] for c in choices][:topk]
        res.body = JSON.dumps(body).encode()

    def pluck(self, req: Request) -> Tuple[Qid, List[Cid]]:
        body = JSON.loads(req.body) if req.body else {}
        if '_nboost' in body:
            qid = Qid(body['_nboost'], 'utf8')
        elif b'_nboost' in req.params:
            qid = req.params[b'_nboost']
        else:
            raise ValueError('_nboost not found')

        if '_id' in body:
            cids = [Cid(body['_id'], 'utf8')]
        elif b'_id' in req.params:
            cids = [Cid(req.params[b'_id'])]
        elif '_ids' in body:
            cids = [Cid(cid) for cid in body['_ids']]
        elif b'_ids' in req.params:
            cids = [Cid(cid) for cid in req.params[b'_ids']]
        else:
            raise ValueError('_id not found')

        return Qid(qid), cids

    def ack(self, qid: Qid, cids: List[Cid]) -> Response:
        cids = [cid.decode() for cid in cids]
        body = JSON.dumps(dict(_nboost=qid.decode(), _ids=cids))
        return Response(b'HTTP/1.1', 200, {}, body.encode())

    def catch(self, e: Exception) -> Response:
        body = JSON.dumps(dict(error=repr(e), type=type(e).__name__)).encode()
        return Response(b'HTTP/1.1', 500, {}, body)

    def pulse(self, state: dict) -> Response:
        return Response(b'HTTP/1.1', 200, {}, pformat(state).encode())

