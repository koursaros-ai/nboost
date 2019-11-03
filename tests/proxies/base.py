from ...base import RouteHandler, Response, BaseServer
from ...proxies import BaseProxy
from ..http import HTTPTestCase


class TestProxy(BaseProxy):
    handler = RouteHandler(BaseProxy.handler)

    @handler.add_route('GET', '/client')
    async def client(self, request):
        async with self.client_handler(
                request.method,
                self.ext_url(request),
                request.content) as client_response:
            return Response.JSON_OK(await client_response.json())


class TestServer(BaseServer):
    handler = RouteHandler(BaseServer.handler)

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

    def test_proxy(self):
        # test server
        res = self.get_from(self.server, path='/server')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

        # test fallback
        res = self.get_from(self.proxy, path='/server')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'server_response')

        # test client
        res = self.get_from(self.proxy, path='/client')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['msg'], 'client_response')

        # test status
        res = self.get_from(self.proxy, path='/status')
        self.assertTrue(res.ok)
        self.assertTrue(res.json()['is_ready'])
        self.assertEqual(res.json()['cls'], TestProxy.__name__)
        self.assertEqual(res.json()['ext_host'], '127.0.0.1')
        self.assertEqual(res.json()['ext_port'], 54001)
        self.assertEqual(res.json()['model'], 'TestModel')
        self.assertEqual(res.json()['traffic']['/server'], 1)
        self.assertEqual(res.json()['traffic']['/client'], 1)

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
