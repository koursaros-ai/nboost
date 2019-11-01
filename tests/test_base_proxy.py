from ..proxies.base import BaseProxy, Response, RouteHandler
from ..cli import set_parser
import unittest
import requests
from pprint import pprint


class TestProxy(BaseProxy):
    handler = RouteHandler()

    @handler.add_route('GET', '/query')
    async def query(self, request):
        return Response.json_200(dict(msg='Success'))


class TestBaseProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--model', 'TestModel'
        ])
        self.url = 'http://%s:%s/' % (args.proxy_host, args.proxy_port)
        self.proxy = TestProxy(args)
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_query(self):
        res = requests.get(self.url + 'query')
        pprint(res.content)
        self.assertTrue(res.ok)

    def test_default(self):
        res = requests.get(self.url + 'unspecified')
        pprint(res.content)
        self.assertTrue(res.ok)

    def tearDown(self):
        self.proxy.kill()
