from nboost.cli import create_proxy
from nboost.server.aio import AioHttpServer
from nboost.base.types import *
import unittest
import requests
import json as JSON
from tests import RESOURCES


class TestProxy(unittest.TestCase):
    def test_default_proxy(self):

        query_json = RESOURCES.joinpath('es_query.json').read_bytes()
        result_json = RESOURCES.joinpath('es_result.json').read_bytes()
        server = AioHttpServer(port=9500, verbose=True)

        async def search(req):
            return Response(b'HTTP/1.1', 200, {}, result_json)

        async def only_on_server(req):
            return Response(b'HTTP/1.1', 200, {}, req.body)

        server.create_app([
            (b'/mock_index/_search', [b'GET'], search),
            (b'/only_on_server', [b'POST'], only_on_server),
        ], not_found_handler=lambda x: x)

        proxy = create_proxy([
            '--port', '8000',
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

        proxy_res = requests.get('http://localhost:8000/mock_index/_search', params=params)
        print(proxy_res.content)
        proxy_json = proxy_res.json()
        self.assertTrue(proxy_res.ok)
        self.assertIsInstance(proxy_json['_nboost'], str)

        server_res = requests.get('http://localhost:9500/mock_index/_search', params=params)
        print(server_res.content)
        self.assertTrue(server_res.ok)

        # train
        json = JSON.dumps(
            dict(_id=proxy_json['hits']['hits'][0]['_id'],
                 _nboost=proxy_json['_nboost'])
        )

        train_res = requests.post('http://localhost:8000/train', data=json)
        self.assertTrue(train_res.ok)

        # test fallback
        fallback_res = requests.post('http://localhost:8000/only_on_server',
                                     data=b'hello there my friend')
        print('fallback:', fallback_res.content)
        self.assertTrue(fallback_res.ok)

        # test status
        status_res = requests.get('http://localhost:8000/status')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())
        # time.sleep(30)

        proxy.close()
        server.stop()