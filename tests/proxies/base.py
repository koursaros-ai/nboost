from ...base import Response, BaseServer
from ...proxies import BaseProxy
from ...clients import TestClient
from ...models import TestModel
from ..http import HTTPTestCase
import time


class TestProxy(BaseProxy, TestClient, TestModel):
    search_path = '/_search'
    train_path = '/_train'


class TestServer(BaseServer):
    @BaseServer.add_route('GET', '/_search')
    async def search(self, request):
        candidates = ['candidate %s' % x for x in range(int(request.query['topk']))]
        return Response.JSON_OK(dict(candidates=candidates))


class TestRankProxy(HTTPTestCase):

    def setUp(self):
        self.topk = 5

        self.server = self.setUpServer(TestServer, ['--port', '54001'])
        self.proxy = self.setUpServer(TestProxy, ['--ext_port', '54001', '--multiplier', '6'])

    def test_search_and_train(self):
        # search
        # params = dict(topk=self.topk, q='test query')
        #
        # proxy_res = self.get_from(self.proxy, path='/_search', params=params)
        # server_res = self.get_from(self.server, path='/_search', params=params)
        #
        # self.assertTrue(proxy_res.ok)
        # self.assertTrue(server_res.ok)
        # self.assertEqual(
        #     len(proxy_res.json()['candidates']),
        #     len(server_res.json()['candidates'])
        # )
        #
        # # train
        # headers = {
        #     'qid': proxy_res.headers['qid'],
        #     'cid': str(self.topk - 1)
        # }
        # train_res = self.get_from(self.proxy, path='/_train', headers=headers)
        # self.assertEqual(train_res.status_code, 204)

        # test status
        res = self.get_from(self.proxy, path='/status')
        self.assertTrue(res.ok)
        self.assertTrue(res.json()['is_ready'])
        self.assertEqual(res.json()['cls'], TestProxy.__name__)
        self.assertEqual(res.json()['ext_host'], '127.0.0.1')
        self.assertEqual(res.json()['ext_port'], 54001)
        self.assertEqual(res.json()['model'], 'TestModel')
        self.assertEqual(res.json()['traffic']['/server'], 1)
        self.assertEqual(res.json()['traffic']['/client'], 1)
        self.assertEqual(res.json()['multiplier'], 6)
        self.assertEqual(len(res.json()['queries']), 1)
        self.assertEqual(res.json()['search_path'], '/_search')
        self.assertEqual(res.json()['train_path'], '/_train')
        # time.sleep(30)

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
