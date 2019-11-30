from nboost.helpers import dump_json, load_json
from nboost.types import Request, Response
from nboost.model.shuffle import ShuffleModel
from nboost.codex.base import BaseCodex
from nboost.server import SocketServer
from nboost.proxy import Proxy
import requests
import unittest


class TestServer(SocketServer):
    def loop(self, client_socket, address):
        response = Response()
        response.body = dump_json(['test choice'] * 10)
        print(response.prepare(Request()))
        client_socket.send(response.prepare(Request()))
        client_socket.close()


class TestCodex(BaseCodex):
    SEARCH_PATH = '/test'

    def parse_query(self, request):
        return request.url.query['q'].split(';')

    def multiply_request(self, request):
        topk = int(request.url.query['topk'])
        request.url.query['topk'] = str(topk * self.multiplier)
        return topk

    def parse_choices(self, response, field):
        return load_json(response.body)

    def reorder_response(self, request, response, ranks):
        response.body = dump_json(load_json(response.body)[:len(ranks)])


class TestProxy(unittest.TestCase):
    def test_proxy(self):

        server = TestServer(port=9500, verbose=True)
        proxy = Proxy(port=8000, model=ShuffleModel, codex=TestCodex,
                      uport=9500, verbose=True)
        proxy.start()
        server.start()
        proxy.is_ready.wait()
        server.is_ready.wait()

        # search
        params = dict(size=5, q='test_field;test query', topk=5)

        proxy_res = requests.get('http://localhost:8000/test', params=params)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)
        self.assertEqual(5, len(proxy_res.json()))

        server_res = requests.get('http://localhost:9500/test', params=params)
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # fallback
        fallback_res = requests.post('http://localhost:8000/only_on_server',
                                     data=b'hello there my friend')
        print('fallback:', fallback_res.content)
        self.assertTrue(fallback_res.ok)

        # status
        status_res = requests.get('http://localhost:8000/nboost')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())

        # invalid host
        proxy.uaddress = ('0.0.0.0', 2000)
        invalid_res = requests.get('http://localhost:8000')
        print(invalid_res.content)
        self.assertFalse(invalid_res.ok)

        proxy.close()
        server.close()
