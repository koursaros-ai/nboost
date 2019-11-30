from nboost.types import Request, Response, URL
from nboost.helpers import dump_json, load_json
from nboost.codex.es import ESCodex
import unittest

REQUEST_URL = URL(b'/test/_search?pretty&q=message:testing&size=15')

REQUEST_BODY = dump_json({
    "size": 100,
    "query": {
        "match": {
            "passage": {
                "query": "this is a test"
            }
        }
    }
})

RESPONSE_BODY = dump_json({
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
            }, {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "0",
                "_score": 1.3862944,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "second choice",
                    "user": "kimchy"
                }
            }
        ]
    }
})


class TestESCodex(unittest.TestCase):
    def test_request_1(self):
        codex = ESCodex(multiplier=8)
        request = Request()
        request.body = REQUEST_BODY
        request.url = URL(b'/test')

        field, query = codex.parse_query(request)
        self.assertEqual(field, 'passage')
        self.assertEqual(query, b'this is a test')
        topk = codex.multiply_request(request)
        self.assertEqual(topk, 100)
        size = load_json(request.body)['size']
        self.assertEqual(size, 800)

    def test_request_2(self):
        codex = ESCodex(multiplier=2)
        request = Request()
        request.url = REQUEST_URL

        field, query = codex.parse_query(request)
        self.assertEqual(field, 'message')
        self.assertEqual(query, b'testing')
        topk = codex.multiply_request(request)
        self.assertEqual(topk, 15)
        self.assertEqual(request.url.query['size'], '30')

    def test_response(self):
        codex = ESCodex()
        request = Request()
        request.url = REQUEST_URL
        response = Response()
        response.body = RESPONSE_BODY

        choices = codex.parse_choices(response, 'message')
        actual_choices = [b'trying out Elasticsearch', b'second choice']
        self.assertEqual(choices, actual_choices)

        codex.reorder_response(request, response, [1, 0])
        body = load_json(response.body)
        self.assertIn('_nboost', body)
        hit = body['hits']['hits'][0]['_source']['message']
        self.assertEqual(hit, 'second choice')
