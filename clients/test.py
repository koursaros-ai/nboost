from .base import BaseClient
from typing import Tuple, List


class TestClient(BaseClient):
    async def query(self, request):
        topk = 3
        response = ES_EXAMPLE_DATA
        response['hits']['hits'] = [response['hits']['hits'][0]] * topk * self.args.multiplier
        candidates = [hit['_source']['message'] for hit in response['hits']['hits']]
        query = 'test query'
        return response, candidates, query, topk

    def reorder(self, response, ranks):
        hits = response['hits']['hits']
        response['hits']['hits'] = [hit for _, hit in sorted(zip(ranks, hits))]

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
