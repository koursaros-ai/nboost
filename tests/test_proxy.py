from proxies.rank import RankProxy
from cli import set_parser
import unittest
import requests
import json
import threading


class TestProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel',
        ])
        proxy = RankProxy(args)
        t = threading.Thread(target=proxy.run)
        t.start()
        self.t = t

    def test_status(self):
        res = requests.get('http://127.0.0.1/status')
        status = json.loads(res)

    def test_query(self):
        pass

    def test_train(self):
        pass

    def tearDown(self):
        pass
