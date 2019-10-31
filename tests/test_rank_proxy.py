from ..cli import set_parser
import unittest
import requests
import json
from .. import models, proxies, clients


class TestRankProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel',
        ])
        self.proxy = proxies['RankProxy'](args)
        self.proxy.start()
        self.url = 'http://%s:%s/' % (args.proxy_host, args.proxy_port)

    def test_status(self):
        res = requests.get(self.url + 'status')
        status = json.loads(res)
        print(status)

    def test_query(self):
        res = requests.get(self.url + 'query')
        print(res)

    def test_train(self):
        res = requests.post(self.url + 'train')
        print(res)

    def tearDown(self):
        self.proxy.stop()
