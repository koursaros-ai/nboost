from neural_rerank.server import BaseServer, ServerHandler
from neural_rerank.cli import create_proxy, set_parser
import unittest
import requests
import time

TOPK = 5


class TestServer(BaseServer):
    handler = ServerHandler(BaseServer.handler)

    @handler.add_route('GET', '/weather')
    def weather(self, request):
        return self.handler.json_ok({'temp': '92F'})

    @handler.add_route('GET', '/search')
    async def search(self, request):
        candidates = ['candidate %s' % x for x in range(int(request.query['topk']))]
        return self.handler.json_ok(candidates)


class TestBaseProxy(unittest.TestCase):

    def setUp(self):

        self.proxy = create_proxy([
            '--client', 'BaseClient',
            '--model', 'BaseModel',
            '--multiplier', '6',
            '--port', '54001',
            '--ext_port', '54001',
            '--verbose'
        ])

        self.proxy.start()
        self.server = TestServer(**vars(set_parser().parse_args([
            '--port', '54001',
            '--verbose'
        ])))
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
        print(proxy_res.headers)
        headers = {
            'qid': proxy_res.headers['qid'],
            'cid': str(TOPK - 1)
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
        import json
        print(json.dumps(status_res.json(), indent=4))
        # self.assertTrue(status_res.json()['is_ready'])
        # self.assertEqual(status_res.json()['ext_host'], '127.0.0.1')
        # self.assertEqual(status_res.json()['ext_port'], 54001)
        # self.assertIn('TestModel', status_res.json()['spec'])
        # self.assertEqual(status_res.json()['multiplier'], 6)
        # self.assertEqual(len(status_res.json()['queries']), 1)
        # self.assertEqual(status_res.json()['search_path'], '/_search')
        # self.assertEqual(status_res.json()['train_path'], '/_train')
        # time.sleep(30)

    def tearDown(self):
        self.server.terminate()
        self.proxy.terminate()
