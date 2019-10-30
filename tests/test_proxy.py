from ..proxy import RankProxy
from ..cli.parser import set_parser
import unittest
import requests
import json


class TestProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel',
        ])
        self.proxy = RankProxy(args)

    def test_status(self):
        res = requests.get('http://127.0.0.1/status')
        status = json.loads(res)

    def test_query(self):
        pass

    def test_train(self):
        pass
