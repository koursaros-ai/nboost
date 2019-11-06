from neural_rerank.server import BaseServer
import unittest
import requests

TOPK = 5


class TestBaseServer(unittest.TestCase):

    def setUp(self):
        self.server = BaseServer(verbose=True)
        self.server.start()
        self.server.is_ready.wait()

    def test_status(self):
        status_res = requests.get('http://%s:%s/status' % (self.server.host, self.server.port))
        self.assertTrue(status_res.ok)

        json = status_res.json()[self.server.__class__.__name__]
        self.assertTrue(json['_is_ready'])
        self.assertEqual(json['_host'], self.server.host)
        self.assertEqual(json['_port'], self.server.port)
        self.assertEqual(json['_read_bytes'], self.server.read_bytes)

    def tearDown(self):
        self.server.close()
