from nboost.helpers import prepare_response
from nboost.models.shuffle import ShuffleModel
from nboost.server import SocketServer
from nboost.proxy import Proxy
from copy import deepcopy
import requests
import unittest


class TestServer(SocketServer):
    def loop(self, client_socket, address):
        client_socket.send(prepare_response(
            request={'headers': {}, 'url': {'query': {'pretty': True}}},
            response=deepcopy(RESPONSE)
        ))
        client_socket.close()


class TestProxy(unittest.TestCase):
    def test_proxy(self):

        server = TestServer(port=9500, verbose=True)
        proxy = Proxy(host='0.0.0.0', port=8000, uhost='0.0.0.0',
                      model=ShuffleModel, uport=9500, bufsize=2048,
                      delim='. ', multiplier=5, verbose=True)
        proxy.start()
        server.start()
        proxy.is_ready.wait()
        server.is_ready.wait()

        # search
        params = dict(q='test_field;test query', size=3)

        proxy_res = requests.get('http://localhost:8000/test/_search', params=params)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)
        self.assertEqual(3, len(proxy_res.json()['hits']['hits']))

        # fallback
        server_res = requests.get('http://localhost:9500/test', params=params)
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # status
        status_res = requests.get('http://localhost:8000/nboost/status')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())
        # self.assertEqual(0.5, status_res.json()['vars']['upstream_mrr']['avg'])

        # invalid host
        proxy.config['uport'] = 2000
        invalid_res = requests.get('http://localhost:8000')
        print(invalid_res.content)
        self.assertFalse(invalid_res.ok)

        proxy.close()
        server.close()


RESPONSE = {
    'headers': {},
    'status': 200,
    'version': 'HTTP/1.1',
    "body": {
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
                    "_score": 1.4,
                    "_source": {
                        "message": "trying out Elasticsearch",
                    }
                }, {
                    "_index": "twitter",
                    "_type": "_doc",
                    "_id": "1",
                    "_score": 1.34245,
                    "_source": {
                        "message": "second result",
                    }
                },
                {
                    "_index": "twitter",
                    "_type": "_doc",
                    "_id": "2",
                    "_score": 1.121234,
                    "_source": {
                        "message": "third result",
                    }
                }
            ]
        }
    }
}