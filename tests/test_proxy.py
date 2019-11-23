from nboost.proxy import SocketServer
from nboost.cli import create_proxy
import requests
import json as JSON
import unittest

DATA = JSON.dumps({
    "took": 5,
    "timed_out": False,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 1.3862944,
        "hits": [
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "0",
                "_score": 1.3862944,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "trying out Elasticsearch",
                    "user": "kimchy"
                }
            }, {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "0",
                "_score": 1.3862944,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "second choice",
                    "user": "kimchy"
                }
            }
        ]
    }
}).encode()
RESPONSE = b'HTTP/1.1 200 OK\r\nContent-Length: %s\r\n\r\n' % str(len(DATA)).encode()
RESPONSE += DATA


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
