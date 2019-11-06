from neural_rerank.server import BaseServer, ServerHandler
from neural_rerank.cli import create_proxy, create_server
from neural_rerank.clients import TestClient
from neural_rerank.models import TestModel
import unittest
import requests
import json
import time

TOPK = 5


class TestServer(BaseServer):
    handler = ServerHandler(BaseServer.handler)

    @handler.add_route('GET', '/weather')
    async def weather(self, request):
        return self.handler.json_ok({'temp': '92F'})

    @handler.add_route('GET', '/search')
    async def search(self, request):
        candidates = ['candidate %s' % x for x in range(int(request.query['topk']))]
        return self.handler.json_ok(candidates)


class TestBaseProxy(unittest.TestCase):

    def setUp(self):

        self.proxy = create_proxy(model_cls=TestModel, client_cls=TestClient, argv=[
            '--multiplier', '6',
            '--ext_port', '54001',
            # '--verbose'
        ])

        self.proxy.start()
        self.server = create_server(cls=TestServer, argv=[
            '--port', '54001',
            # '--verbose'
        ])

        self.server.start()
        self.server.is_ready.wait()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        # search
        params = dict(topk=TOPK, q='test query')

        proxy_res = requests.get(
            'http://%s:%s/search' % (self.proxy.host, self.proxy.port),
            params=params
        )

        server_res = requests.get(
            'http://%s:%s/search' % (self.server.host, self.server.port),
            params=params
        )

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)

        # num candidates should be equal
        self.assertEqual(len(proxy_res.json()), len(server_res.json()))
        
        # train
        data = json.dumps({
            'qid': proxy_res.headers['qid'],
            'cid': str(TOPK - 1)
        })

        train_res = requests.post(
            'http://%s:%s/train' % (self.proxy.host, self.proxy.port),
            data=data
        )
        self.assertEqual(train_res.status_code, 204)

        # test fallback
        stream_proxy_res = requests.get(
            'http://%s:%s/weather' % (self.proxy.host, self.proxy.port)
        )
        self.assertEqual(stream_proxy_res.json()['temp'], '92F')

        # test fallback
        fallback_res = requests.get(
            'http://%s:%s/hello' % (self.proxy.host, self.proxy.port)
        )
        self.assertEqual(fallback_res.status_code, 404)

        # test status
        status_res = requests.get(
            'http://%s:%s/status' % (self.proxy.host, self.proxy.port)
        )
        self.assertTrue(status_res.ok)
        print(json.dumps(status_res.json(), indent=4))
        self.assertEqual(status_res.json()['TestClient']['ext_host'], self.proxy.client.ext_host)
        # self.assertEqual(status_res.json()['ext_port'], 54001)
        # self.assertIn('TestModel', status_res.json()['spec'])
        # self.assertEqual(status_res.json()['multiplier'], 6)
        # self.assertEqual(len(status_res.json()['queries']), 1)
        # self.assertEqual(status_res.json()['search_path'], '/_search')
        # self.assertEqual(status_res.json()['train_path'], '/_train')
        # time.sleep(30)

    def tearDown(self):
        self.server.close()
        self.proxy.close()
        self.assertFalse(self.server.is_ready.is_set())
        self.assertFalse(self.proxy.is_ready.is_set())
