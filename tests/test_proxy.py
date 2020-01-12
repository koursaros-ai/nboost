
from pprint import pprint
import unittest
import requests
from nboost.helpers import prepare_response, dump_json
from nboost.server import SocketServer
from nboost.session import Session
from nboost.proxy import Proxy


class TestServer(SocketServer):
    def loop(self, client_socket, address):
        session = Session()
        session.response['body'] = dump_json(RESPONSE)
        prepared_response = prepare_response(session.response)
        client_socket.send(prepared_response)
        client_socket.close()


class TestProxy(unittest.TestCase):
    def test_proxy(self):
        server = TestServer(port=9500, verbose=True)
        proxy = Proxy(model_dir='shuffle-model', model='ShuffleModel', uport=9500,
                      verbose=True, query_prep='lambda query: query.split(";")[-1]')
        proxy.start()
        server.start()
        proxy.is_ready.wait()
        server.is_ready.wait()

        # search
        proxy_res = requests.get(
            'http://localhost:8000/test/_search',
            params={
                'q': 'test_field;test query',
                'size': 3,
                'debug': True,
                'topn': 20
            }
        )
        self.assertTrue(proxy_res.ok)
        pprint(proxy_res.json())
        session = proxy_res.json()['nboost']
        self.assertEqual('test query', session['query'])
        self.assertEqual(3, session['topk'])
        self.assertEqual(20, session['topn'])
        self.assertEqual(3, len(session['cvalues']))

        # fallback
        server_res = requests.get('http://localhost:9500/test')
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # status
        status_res = requests.get('http://localhost:8000/nboost/status')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())

        # invalid host
        invalid_res = requests.get('http://localhost:8000', params={'uport': 2000})
        print(invalid_res.content)
        self.assertFalse(invalid_res.ok)

        proxy.close()
        server.close()


RESPONSE = {
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
