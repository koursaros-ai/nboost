from json.decoder import JSONDecodeError
from ..base import BaseProtocol
from ..base.types import URL
from typing import List
import json as JSON


class ElasticsearchError(Exception):
    pass


class ESProtocol(BaseProtocol):
    SEARCH_PATH = '/.*/_search'
    SEARCH_METHODS = ['GET', 'POST']

    def on_request_url_and_method(self):
        if 'size' in self.request.url.query:
            self.topk = int(self.request.url.query['size'])
            self.request.url.query['size'] = str(self.topk * self.multiplier)

        if 'q' in self.request.url.query:
            q = self.request.url.query['q']
            self.query = q[q.find(':') + 1:]

    def on_request_message_complete(self):
        try:
            json = JSON.loads(self.request.body)

            try:
                self.topk = json['size']
                json['size'] *= self.multiplier
            except KeyError:
                pass

            try:
                inner = json['collapse']['inner_hits']
                self.topk = inner['size']
                inner['size'] *= self.multiplier
            except KeyError:
                pass

            if not self.topk:
                self.topk = 10
                self.request.url.query['size'] = str(self.topk * self.multiplier)

            try:
                self.query = json['query']['match'][self.field]
                if isinstance(self.query, dict):
                    self.query = self.query['query']
            except KeyError:
                pass

        except JSONDecodeError:
            pass

        if self.query is None:
            raise ValueError('Missing query')

    def on_response_status(self, status: int):
        if status >= 400:
            self.error = ElasticsearchError(self.request.body)

    def on_response_message_complete(self):
        print(self.response.body)
        self.response.body = JSON.loads(self.response.body)
        hits = self.response.body.get('hits', [])
        self.choices = [hit['_source'][self.field] for hit in hits['hits']]

    def on_rank(self, ranks: List[int]):
        self.response.body['_nboost'] = True
        hits = self.response.body['hits']
        hits['hits'] = [hits['hits'][rank] for rank in ranks][:self.topk]
        self.response.body = JSON.dumps(self.response.body).encode()

    def on_error(self, e: Exception):
        self.response.body = JSON.dumps(dict(error=repr(e))).encode()
        self.response.status = 500

