from nboost.proxy import SocketServer
from nboost.cli import create_proxy
from tests.test_es_protocol import RESPONSE
import requests
import unittest


class TestServer(SocketServer):
    def loop(self, client_socket, address):
        client_socket.send(RESPONSE)
        client_socket.close()


class TestProxy(unittest.TestCase):
    def test_default_proxy(self):

        server = TestServer(port=9500, verbose=True)
        proxy = create_proxy([
            '--port', '8000',
            '--model', 'TestModel',
            '--field', 'message',
            '--uport', '9500',
            '--verbose'
        ])
        proxy.start()
        server.start()
        proxy.is_ready.wait()
        server.is_ready.wait()

        # search
        params = dict(size=5, q='test:test query', pretty='')

        proxy_res = requests.get('http://localhost:8000/mock_index/_search', params=params)
        print(proxy_res.content)
        proxy_json = proxy_res.json()
        self.assertTrue(proxy_res.ok)
        self.assertIn('_nboost', proxy_json)

        server_res = requests.get('http://localhost:9500/mock_index/_search', params=params)
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
        proxy.uaddress = ('localhost', 2000)
        invalid_res = requests.get('http://localhost:8000')
        print(invalid_res.content)
        self.assertFalse(invalid_res.ok)

        proxy.close()
        server.close()
