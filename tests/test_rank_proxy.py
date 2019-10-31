from ..cli import set_parser
import unittest
import requests
from .. import proxies
from pprint import pprint


class TestRankProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel'
        ])
        self.url = 'http://%s:%s/' % (args.proxy_host, args.proxy_port)
        self.proxy = getattr(proxies, 'RankProxy')(args)
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_status(self):
        res = requests.get(self.url + 'status')
        pprint(res.json())
        self.assertTrue(res.ok)

    def test_query(self):
        res = requests.get(self.url + 'query')
        pprint(res.json())
        self.assertTrue(res.ok)
        qid = res.json()['qid']

        res = requests.post(self.url + 'train/?qid=' + str(qid))
        pprint(res.json())
        self.assertTrue(res.ok)

    def tearDown(self):
        self.proxy.kill()
