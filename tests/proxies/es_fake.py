from ...base import BaseServer, RouteHandler, Response
from ...proxies.rank import ESProxy
from ..http import HTTPTestCase
import copy


class FakeESServer(BaseServer):
    handler = RouteHandler(BaseServer.handler)

    @handler.add_route('GET', '/{index}/_search')
    async def search(self, request):
        response = copy.deepcopy(FAKE_ES_DATA)
        response['hits']['hits'] = [FAKE_ES_HIT] * int(request.query['size'])
        return Response.JSON_OK(response)


class TestESProxy(HTTPTestCase):

    def setUp(self):
        self.topk = 5
        self.es_index = 'test_index'

        self.server = self.setUpServer(FakeESServer, ['--port', '9200'])
        self.proxy = self.setUpServer(ESProxy, [
            '--model', 'TestModel',
            '--ext_port', '9200',
            '--field', 'message'
        ])

    def test_search_and_train(self):
        # search
        params = dict(size=self.topk, q='message:test query')

        proxy_res = self.send(
            'GET',
            host=self.proxy.host,
            port=self.proxy.port,
            path='/%s/_search' % self.es_index,
            params=params)
        server_res = self.send(
            'GET',
            host=self.server.host,
            port=self.server.port,
            path='/%s/_search' % self.es_index,
            params=params)

        proxy_candidates = proxy_res.json()['hits']['hits']
        server_candidates = server_res.json()['hits']['hits']

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)
        self.assertEqual(len(proxy_candidates), len(server_candidates))

        # train
        headers = dict(qid=proxy_res.headers['qid'], cid=str(self.topk - 1))
        train_res = self.send(
            'GET',
            host=self.proxy.host,
            port=self.proxy.port,
            path='/train',
            headers=headers)

        self.assertTrue(train_res.ok)

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()


FAKE_ES_DATA = {
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
        "hits": []
    }
}

FAKE_ES_HIT = {
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