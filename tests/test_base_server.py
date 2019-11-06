from neural_rerank.cli import create_server
import unittest
import requests
import time

TOPK = 5


class TestBaseServer(unittest.TestCase):

    def setUp(self):
        self.server = create_server(argv=['--verbose'])
        self.server.start()
        self.server.is_ready.wait()

    def test_status(self):
        status_res = requests.get('http://%s:%s/status' % (self.server.host, self.server.port))
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
        self.server.close()
