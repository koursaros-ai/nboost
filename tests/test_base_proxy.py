from ..base import RouteHandler, Response, BaseServer
from ..cli import set_parser
from ..proxies import BaseProxy
import unittest
import requests
from pprint import pprint


class TestProxy(BaseProxy):
    handler = RouteHandler()

    @handler.add_route('GET', '/proxy')
    async def proxy(self, request):
        return Response.json_200(dict(msg='proxy_route'))


class TestServer(BaseServer):
    handler = RouteHandler()

    @handler.add_route('GET', '/server')
    async def server(self, request):
        return Response.json_200(dict(msg='server_route'))


class TestBaseProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--port', '54001'
        ])
        self.server = TestServer(**vars(args))
        self.server.start()
        self.server.is_ready.wait()

        args = parser.parse_args([
            '--verbose',
            '--model', 'TestModel',
            '--ext_port', '54001'
        ])
        # return f(**vars(p_args))
        self.proxy = TestProxy(**vars(args))
        self.proxy.start()
        self.url = 'http://%s:%s/' % (self.proxy.host, self.proxy.port)
        self.proxy.is_ready.wait()

    def test_query(self):
        res = requests.get(self.url + 'proxy')
        pprint(res.content)
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'proxy_route')

    def test_default(self):
        res = requests.get(self.url + 'server')
        pprint(res.content)
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_route')

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()

