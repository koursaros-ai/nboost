
from neural_rerank.cli import create_proxy, create_server
from neural_rerank.clients import ESClient
from neural_rerank.models import TestModel
from neural_rerank.server import BaseServer, ServerHandler
import unittest
import requests
import copy
import time

TOPK = 5
ES_INDEX = 'test_index'


class MockESServer(BaseServer):
    handler = ServerHandler(BaseServer.handler)

    @handler.add_route('GET', '/{index}/_search')
    async def search(self, request):
        response = copy.deepcopy(MOCK_ES_DATA)
        response['hits']['hits'] = [MOCK_ES_HIT] * int(request.query['size'])
        return self.handler.json_ok(response)


class TestESProxy(unittest.TestCase):

    def setUp(self):
        self.proxy = create_proxy(model_cls=TestModel, client_cls=ESClient, argv=[
            '--ext_port', '9500',
            '--field', 'message',
            '--verbose'
        ])
        self.proxy.start()
        self.server = create_server(cls=MockESServer, argv=[
            '--port', '9500',
            '--verbose'
        ])
        self.server.start()
        self.server.is_ready.wait()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        # search
        params = dict(size=TOPK, q='message:test query')

        proxy_res = requests.get(
            'http://%s:%s/%s/_search' % (self.proxy.host, self.proxy.port, ES_INDEX),
            params=params
        )
        server_res = requests.get(
            'http://%s:%s/%s/_search' % (self.server.host, self.server.port, ES_INDEX),
            params=params
        )

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)
        self.assertEqual(
            len(proxy_res.json()['hits']['hits']),
            len(server_res.json()['hits']['hits'])
        )

        # train
        headers = dict(qid=proxy_res.headers['qid'], cid=str(TOPK - 1))
        train_res = requests.get(
            'http://%s:%s/train' % (self.proxy.host, self.proxy.port),
            headers=headers
        )
        # time.sleep(30)
        self.assertTrue(train_res.ok)

    def tearDown(self):
        self.server.close()
        self.proxy.close()


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