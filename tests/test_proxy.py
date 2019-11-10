from nboost.cli import create_proxy
from nboost.server import AioHttpServer
from nboost.paths import RESOURCES
from nboost.base.types import *
import unittest
import requests
import json as JSON

from elasticsearch import Elasticsearch


class TestProxy(unittest.TestCase):
    def test_default_proxy(self):
        query_json = RESOURCES.joinpath('es_query.json').read_bytes()
        result_json = RESOURCES.joinpath('es_result.json').read_bytes()
        server = AioHttpServer(port=9500, verbose=True)

        async def search(req):
            return Response({}, result_json, 200)

        async def only_on_server(req):
            return Response({}, req.body, 200)

        not_found_handler = lambda x: x
        server.create_app([
            ({'/mock_index/_search': ['GET']}, search),
            ({'/only_on_server': ['POST']}, only_on_server),
        ], not_found_handler)

        proxy = create_proxy([
            '--model', 'TestModel',
            '--field', 'message',
            '--ext_port', '9500',
            '--verbose'
        ])
        proxy.start()
        server.start()
        server.is_ready.wait()

        # search
        params = dict(size=5, q='test query')

        proxy_res = requests.get('http://localhost:53001/mock_index/_search', params=params)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)

        server_res = requests.get('http://localhost:9500/mock_index/_search', params=params)
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # train
        proxy_json = proxy_res.json()
        json = JSON.dumps(
            dict(cid=proxy_json['hits']['hits'][0]['cid'],
                 qid=proxy_json['qid'])
        )

        train_res = requests.post('http://localhost:53001/train', data=json)
        self.assertTrue(train_res.ok)

        # test fallback
        fallback_res = requests.post('http://localhost:53001/only_on_server')
        print(fallback_res.content)
        self.assertTrue(fallback_res.ok)

        # test status
        status_res = requests.get('http://localhost:53001/status')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())
        # time.sleep(30)

        proxy.close()
        server.stop()

    def test_match_query(self):
        es = Elasticsearch(host='localhost',post=53001)
        res = es.search(index='mock_index', body={
            "size": 10,
            "query": {
                "match": {
                    "passage": {
                        "query": 'This is a test'
                    }
                }
            }
        }, filter_path=['hits.hits._*'])