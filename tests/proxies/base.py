from neural_rerank.base import Response, BaseServer, Handler
from neural_rerank.proxies import BaseProxy
from neural_rerank.clients import TestClient
from neural_rerank.models import TestModel
from ..http import HTTPTestCase
import time


class TestProxy(BaseProxy, TestClient, TestModel):
    search_path = '/_search'
    train_path = '/_train'


class TestServer(BaseServer):
    handler = Handler(BaseServer.handler)

    @handler.add_route('GET', '/_search')
    async def search(self, request):
        candidates = ['candidate %s' % x for x in range(int(request.query['topk']))]
        return Response.JSON_OK(candidates)


class TestBaseProxy(HTTPTestCase):

    def setUp(self):
        self.topk = 5

        self.server = self.setUpServer(TestServer, ['--port', '54001'])
        self.proxy = self.setUpServer(TestProxy, ['--ext_port', '54001', '--multiplier', '6'])

    def test_search_and_train(self):
        # search
        params = dict(topk=self.topk, q='test query')

        proxy_res = self.get_from(self.proxy, path='/_search', params=params)
        server_res = self.get_from(self.server, path='/_search', params=params)

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)

        # num candidates should be equal
        self.assertEqual(len(proxy_res.json()), len(server_res.json()))

        # train
        headers = {
            'qid': proxy_res.headers['qid'],
            'cid': str(self.topk - 1)
        }
        train_res = self.get_from(self.proxy, path='/_train', headers=headers)
        self.assertEqual(train_res.status_code, 204)

        # test status
        # time.sleep(30)
        res = self.get_from(self.proxy, path='/status')
        self.assertTrue(res.ok)
        self.assertTrue(res.json()['is_ready'])
        self.assertEqual(res.json()['spec'][0], TestProxy.__name__)
        self.assertEqual(res.json()['ext_host'], '127.0.0.1')
        self.assertEqual(res.json()['ext_port'], 54001)
        self.assertIn('TestModel', res.json()['spec'])
        self.assertEqual(res.json()['multiplier'], 6)
        self.assertEqual(len(res.json()['queries']), 1)
        self.assertEqual(res.json()['search_path'], '/_search')
        self.assertEqual(res.json()['train_path'], '/_train')

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
