from typing import Tuple, List
from pprint import pformat
from ..base import *
from json.decoder import JSONDecodeError


class ElasticsearchError(Exception):
    pass


class ESCodex(BaseCodex):
    SEARCH = ('/.*/_search', ['GET'])

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
            return Topk(req.params['size'])
        except KeyError:
            pass

        # if not in params and no req body then return default
        try:
            json = req.json
        except JSONDecodeError:
            return Topk(10)

        try:
            return Topk(json['size'])
        except KeyError:
            pass

        try:
            return Topk(json['collapse']['inner_hits']['size'])
        except KeyError:
            pass

        # if size is not found
        return Topk(10)

    def magnify(self, req: Request, topk: Topk) -> None:
        mtopk = topk * self.multiplier
        topk_is_set = False

        if req.body:
            json = req.json

            if 'size' in json:
                json['size'] = mtopk
                topk_is_set = True

            try:
                # if it's in inner hits set to topk
                _ = json['collapse']['inner_hits']['size']
                json['collapse']['inner_hits']['size'] = mtopk
                topk_is_set = True
            except KeyError:
                pass

            req.json = json

        if not topk_is_set:
            req.params['size'] = str(mtopk)

    def parse(self, req: Request, res: Response) -> Tuple[Query, List[Choice]]:
        if res.status >= 400:
            raise ElasticsearchError(res.body)

        query = None

        if 'q' in req.params:
            query = req.params['q']
            query = query[query.find(':') + 1:]

        try:
            json = req.json
            try:
                query = json['query']['match'][self.field]
                if isinstance(query, dict):
                    query = query['query']
            except KeyError:
                pass

        except JSON.JSONDecodeError:
            pass

        if query is None:
            raise ValueError('Missing query')

        hits = res.json.get('hits', [])
        choices = []
        for hit in hits.get('hits', []):
            choices += [Choice(
                hit['_source'][self.field].encode(), ident=hit['_id'].encode()
            )]

        return Query(query.encode()), choices

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
        body = req.json if req.body else {}
        if '_nboost' in body:
            qid = body['_nboost']
        elif '_nboost' in req.params:
            qid = req.params['_nboost']
        else:
            raise ValueError('_nboost not found')

        if '_id' in body:
            cids = [body['_id']]
        elif '_id' in req.params:
            cids = [req.params['_id']]
        elif '_ids' in body:
            cids = body['_ids']
        elif '_ids' in req.params:
            cids = req.params['_ids']
        else:
            raise ValueError('_id not found')

        return Qid(qid, 'utf8'), [Cid(cid, 'utf8') for cid in cids]

    def ack(self, qid: Qid, cids: List[Cid]) -> Response:
        cids = [cid.decode() for cid in cids]
        response = Response()
        response.json = dict(_nboost=qid.decode(), _ids=cids)
        return response

    def catch(self, e: Exception) -> Response:
        response = Response()
        response.json = dict(error=repr(e), type=type(e).__name__)
        response.status = 500
        return response

    def pulse(self, state: dict) -> Response:
        return Response(body=pformat(state).encode())

