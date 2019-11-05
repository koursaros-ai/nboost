from neural_rerank.base import Response, BaseServer, Handler
from neural_rerank.proxies import BaseProxy
from neural_rerank.clients import TestClient
from neural_rerank.models import TestModel
from neural_rerank.cli import set_parser
import unittest
import requests
import time


class TestProxy(BaseProxy, TestClient, TestModel):
    _search_path = '/_search'
    _train_path = '/_train'


class TestServer(BaseServer):
    handler = Handler(BaseServer.handler)

    @handler.add_route('GET', '/_search')
    async def search(self, request):
        candidates = ['candidate %s' % x for x in range(int(request.query['topk']))]
        return Response.JSON_OK(candidates)


class TestBaseProxy(unittest.TestCase):

    def setUp(self):
        self.topk = 5
        parser = set_parser()
        self.server = TestServer(**vars(parser.parse_args([
            '--port', '54001',
            '--verbose'
        ])))
        self.proxy = TestProxy(**vars(parser.parse_args([
            '--ext_port', '54001',
            '--multiplier', '6',
            '--verbose'
        ])))

        self.server.start()
        self.proxy.start()
        self.server.is_ready.wait()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        # search
        params = dict(topk=self.topk, q='test query')

        proxy_res = requests.get(
            'http://%s:%s/_search' % (self.proxy.host, self.proxy.port),
            params=params
        )

        server_res = requests.get(
            'http://%s:%s/_search' % (self.server.host, self.server.port),
            params=params
        )

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)

        # num candidates should be equal
        self.assertEqual(len(proxy_res.json()), len(server_res.json()))

        # train
        print(proxy_res.headers)
        headers = {
            'qid': proxy_res.headers['qid'],
            'cid': str(self.topk - 1)
        }

        train_res = requests.get(
            'http://%s:%s/_train' % (self.proxy.host, self.proxy.port),
            headers=headers
        )
        self.assertEqual(train_res.status_code, 204)

        # test status
        status_res = requests.get(
            'http://%s:%s/status' % (self.proxy.host, self.proxy.port)
        )
        self.assertTrue(status_res.ok)
        self.assertTrue(status_res.json()['is_ready'])
        self.assertEqual(status_res.json()['spec'][0], TestProxy.__name__)
        self.assertEqual(status_res.json()['ext_host'], '127.0.0.1')
        self.assertEqual(status_res.json()['ext_port'], 54001)
        self.assertIn('TestModel', status_res.json()['spec'])
        self.assertEqual(status_res.json()['multiplier'], 6)
        self.assertEqual(len(status_res.json()['queries']), 1)
        self.assertEqual(status_res.json()['search_path'], '/_search')
        self.assertEqual(status_res.json()['train_path'], '/_train')
        # time.sleep(30)

    def tearDown(self):
        self.server.terminate()
        self.proxy.terminate()
