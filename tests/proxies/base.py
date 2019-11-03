from ...base import RouteHandler, Response, BaseServer
from ...proxies import BaseProxy
from ..http import HTTPTestCase


class TestProxy(BaseProxy):
    handler = RouteHandler()

    @handler.add_route('GET', '/client')
    async def client(self, request):
        async with self.client_handler(
                request.method,
                self.ext_url(request),
                request.content) as client_response:
            return Response.JSON_OK(await client_response.json())


class TestServer(BaseServer):
    handler = RouteHandler()

    @handler.add_route('GET', '/server')
    async def server(self, request):
        return Response.JSON_OK(dict(msg='server_response'))

    @handler.add_route('GET', '/client')
    async def client(self, request):
        return Response.JSON_OK(dict(msg='client_response'))


class TestBaseProxy(HTTPTestCase):

    def setUp(self):
        self.server = self.setUpServer(TestServer, ['--port', '54001'])
        self.proxy = self.setUpServer(TestProxy, [
            '--model', 'TestModel',
            '--ext_port', '54001'
        ])

    def test_server(self):
        res = self.send(
            'GET', host=self.server.host, port=self.server.port, path='/server')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

    def test_proxy_fallback(self):
        res = self.send(
            'GET', host=self.proxy.host, port=self.proxy.port, path='/server')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

    def test_proxy_client(self):
        res = self.send(
            'GET', host=self.proxy.host, port=self.proxy.port, path='/client')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'client_response')

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
