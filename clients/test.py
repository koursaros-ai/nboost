from .base import BaseClient
from typing import Tuple, List


class TestClient(BaseClient):
    def query(self, request):
        response = ES_EXAMPLE_DATA
        candidates = [response['hits']['hits'][0]['_source'][self.args.field]]
        candidates *= 10 * self.args.multiplier
        query = 'test query'
        return response, candidates, query

    def reorder(self, response, ranks):
        response['hits']['hits'] = response['hits']['hits'][:self.args.topk]
        return response


ES_EXAMPLE_DATA = {
    "took": 5,
    "timed_out": False,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 1.3862944,
        "hits": [
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "0",
                "_score": 1.3862944,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "trying out Elasticsearch",
                    "user": "kimchy"
                }
            }
        ]
    }
}
