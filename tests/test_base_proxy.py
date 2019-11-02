from ..base import RouteHandler, Response, BaseServer
from ..cli import set_parser
from ..proxies import BaseProxy
import unittest
import requests


class TestProxy(BaseProxy):
    handler = RouteHandler()

    @handler.add_route('GET', '/client')
    async def client(self, request):
        async with self.client_handler(
                request.method,
                self.ext_url(request),
                request.content) as client_response:

            return Response.plain_200(await client_response.read())


class TestServer(BaseServer):
    handler = RouteHandler()

    @handler.add_route('GET', '/server')
    async def server(self, request):
        return Response.json_200(dict(msg='server_response'))

    @handler.add_route('GET', '/client')
    async def client(self, request):
        return Response.json_200(dict(msg='client_response'))


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
        self.proxy.is_ready.wait()

    def test_server(self):
        res = requests.get(self.server.url + '/server')
        self.proxy.logger.info('%s:%s' % (res.status_code, res.content))
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

    def test_proxy_fallback(self):
        res = requests.get(self.proxy.url + '/server')
        self.proxy.logger.info('%s:%s' % (res.status_code, res.content))
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

    def test_proxy_client(self):
        res = requests.get(self.proxy.url + '/client')
        self.proxy.logger.info('%s:%s' % (res.status_code, res.content))
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'client_response')

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
