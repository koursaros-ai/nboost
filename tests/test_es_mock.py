from neural_rerank.base import BaseServer, Handler, Response
from neural_rerank.proxies import ESProxy
from neural_rerank.cli import set_parser
import unittest
import requests
import copy
import time


class MockESServer(BaseServer):
    handler = Handler(BaseServer.handler)

    @handler.add_route('GET', '/{index}/_search')
    async def search(self, request):
        response = copy.deepcopy(MOCK_ES_DATA)
        response['hits']['hits'] = [MOCK_ES_HIT] * int(request.query['size'])
        return Response.JSON_OK(response)


class TestESProxy(unittest.TestCase):

    def setUp(self):
        self.topk = 5
        self.es_index = 'test_index'
        parser = set_parser()

        self.server = MockESServer(**vars(parser.parse_args([
            '--port', '9500',
            '--verbose'
        ])))
        self.proxy = ESProxy(**vars(parser.parse_args([
            '--ext_port', '9500',
            '--field', 'message',
            '--verbose'
        ])))

        self.server.start()
        self.proxy.start()
        self.server.is_ready.wait()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        # search
        params = dict(size=self.topk, q='message:test query')

        proxy_res = requests.get(
            'http://%s:%s/%s/_search' % (self.proxy.host, self.proxy.port, self.es_index),
            params=params
        )
        server_res = requests.get(
            'http://%s:%s/%s/_search' % (self.server.host, self.server.port, self.es_index),
            params=params
        )

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)
        self.assertEqual(
            len(proxy_res.json()['hits']['hits']),
            len(server_res.json()['hits']['hits'])
        )

        # train
        headers = dict(qid=proxy_res.headers['qid'], cid=str(self.topk - 1))
        train_res = requests.get(
            'http://%s:%s/train' % (self.server.host, self.server.port),
            headers=headers
        )
        time.sleep(30)
        print(train_res)
        self.assertTrue(train_res.ok)

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()


MOCK_ES_DATA = {
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
        "hits": []
    }
}

MOCK_ES_HIT = {
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