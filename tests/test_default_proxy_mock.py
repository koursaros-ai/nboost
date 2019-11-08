from neural_rerank.cli import create_proxy
from tests.test_test_server import TestServer
import unittest
import requests
import json as JSON


class TestProxy(unittest.TestCase):
    def test_default_proxy(self):
        proxy = create_proxy([
            '--field', 'message',
            '--ext_port', '9500',
            '--verbose'
        ])
        server = TestServer(
            ('GET', '/mock_index/_search', lambda: MOCK_ES_DATA),
            ('GET', '/_stats', lambda: {'fake': 'statistics'}), port=9500
        )
        proxy.enter()
        server.enter()

        # search
        params = dict(size=5, q='test query')

        proxy_res = requests.get('http://localhost:53001/mock_index/_search', params=params, stream=True)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)

        server_res = requests.get('http://localhost:9500/mock_index/_search', params=params)
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # num choices should be equal
        body = proxy_res.json()
        self.assertEqual(len(body), len(server_res.json()))

        # train
        json = JSON.dumps(
            dict(cid=proxy_res.json()['hits']['hits'][0]['cid'])
        )

        train_res = requests.post('http://localhost:53001/train', data=json)
        self.assertTrue(train_res.ok)

        # test fallback
        fallback_res = requests.get('http://localhost:53001/_stats')
        print(fallback_res.content)
        self.assertTrue(fallback_res.ok)

        # test status
        status_res = requests.get('http://localhost:53001/status')
        self.assertTrue(status_res.ok)
        print(JSON.dumps(status_res.json(), indent=4))
        # time.sleep(30)

        proxy.exit()
        server.exit()
        self.assertFalse(proxy.is_ready.is_set())


MOCK_ES_DATA = {
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
            }
        ]
    }
}