from typing import List, Tuple, Any
from contextlib import suppress
from nboost.types import Request, Response, Choice
from nboost.helpers import load_json, dump_json
from nboost.exceptions import MissingQuery
from nboost.codex.base import BaseCodex


class ESCodex(BaseCodex):
    """Elasticsearch Codex"""
    SEARCH_PATH = '/.*/_search'

    def parse_query(self, request: Request) -> Tuple[Any, bytes]:
        """try to get query from query params, then body"""
        body = load_json(request.body)

        # search for query in body
        if body:
            with suppress(KeyError):
                field, query = body['query']['match'].popitem()
                if isinstance(query, dict):
                    query = query['query']
                return field, query.encode()

        # search for query in url
        with suppress(KeyError):
            field, *query = request.url.query['q'].split(':')
            return field, ':'.join(query).encode()

        raise MissingQuery

    def multiply_request(self, request: Request) -> Tuple[int, List[str]]:
        """Multiply size of Elasticsearch query"""
        body = load_json(request.body)

        topk = request.url.query.pop('size', None)
        correct_cids = request.url.query.pop('nboost', None)

        # search for topk in body
        if body:
            correct_cids = body.pop('nboost', correct_cids)
            topk = body.pop('size', topk)

        topk = 10 if topk is None else int(topk)

        if body:
            body['size'] = topk * self.multiplier
            request.body = dump_json(body)
        else:
            request.url.query['size'] = str(topk * self.multiplier)

        correct_cids = correct_cids.split(',') if correct_cids else None
        return topk, correct_cids

    def parse_choices(self, response: Response, field: str) -> List[Choice]:
        """Parse out Elasticsearch hits"""
        body = load_json(response.body)
        hits = body.get('hits', {'hits': []})['hits']
        return [Choice(
            hit['_id'],  # cid
            hit['_source'][field].encode()  # body
        ) for hit in hits]

    def reorder_response(self, request, response, ranks):
        """Reorder Elasticsearch hits"""
        body = load_json(response.body)
        body['_nboost'] = '⚡NBOOST'

        body['hits']['hits'] = [body['hits']['hits'][rank] for rank in ranks]

        jkwargs = {'ensure_ascii': False}
        if 'pretty' in request.url.query:
            jkwargs.update({'indent': 2})

        response.body = dump_json(body, **jkwargs)
