from nboost.base import RequestHandler, ResponseHandler
from nboost.base.types import RawHttpMessage
from nboost.protocol.es import ESProtocol
import json as JSON
import unittest

REQUEST = RawHttpMessage(
    'GET /test/_search?pretty&q=message:testing&size=20 HTTP/1.1',
    [],
    ''
)

REQUEST_2 = RawHttpMessage(
    'POST /test/_search HTTP/1.1',
    [],
    JSON.dumps({
        "from": 0, "size": 20,
        "query": {
            "term": {"user": "kimchy"}
        }
    })
)

REQUEST_3 = RawHttpMessage(
    'POST /test/_search HTTP/1.1',
    [],
    JSON.dumps({
        "size": 100,
        "query": {
            "match": {
                "passage": {
                    "query": "this is a test"
                }
            }
        }
    })
)

RESPONSE = RawHttpMessage(
    'HTTP/1.1 200 OK',
    [],
    JSON.dumps({
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
)


class TestESCodex(unittest.TestCase):

    def test_request(self):
        protocol = ESProtocol(multiplier=5, field='message')
        request_handler = RequestHandler(protocol)

        request_handler.feed(REQUEST)
        self.assertEqual(protocol.topk, 20)
        self.assertEqual(protocol.request.url.query['size'], '100')
        self.assertIn('pretty', protocol.request.url.query)
        self.assertEqual(protocol.query, 'testing')

    def test_request_2(self):
        protocol = ESProtocol(multiplier=5, field='user')
        request_handler = RequestHandler(protocol)
        request_handler.feed(REQUEST_2)

        self.assertEqual(protocol.topk, 20)
        self.assertEqual(protocol.query, 'kimchy')

    def test_request_3(self):
        protocol = ESProtocol(multiplier=5, field='passage')
        request_handler = RequestHandler(protocol)

        request_handler.feed(REQUEST_3)
        self.assertEqual(protocol.topk, 100)
        self.assertEqual(protocol.query, 'this is a test')

    def test_response(self):
        protocol = ESProtocol(multiplier=5, field='message')
        response_handler = ResponseHandler(protocol)

        response_handler.feed(RESPONSE)
        self.assertEqual(protocol.choices,
                         ['trying out Elasticsearch', 'second choice'])

        protocol.on_error(ValueError('This is an exception'))
        self.assertEqual(protocol.response.status, 500)
