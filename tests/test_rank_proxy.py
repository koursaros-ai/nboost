from ..cli import set_parser
import unittest
import requests
from .. import proxies
from pprint import pprint


class TestRankProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel'
        ])
        self.url = 'http://%s:%s/' % (args.proxy_host, args.proxy_port)
        self.proxy = getattr(proxies, 'RankProxy')(args)
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_status(self):
        res = requests.get(self.url + 'status')
        pprint(res.json())
        self.assertTrue(res.ok)

    def test_query(self):
        res = requests.get(self.url + 'query')
        pprint(res.json())
        self.assertTrue(res.ok)
        qid = res.json()['qid']

        res = requests.post(self.url + 'train/?qid=' + str(qid))
        pprint(res.json())
        self.assertTrue(res.ok)

    def tearDown(self):
        self.proxy.kill()


#     @routes.get('/query')
#     async def query(self, request):
#         topk = 3
#         response = ES_EXAMPLE_DATA
#         response['hits']['hits'] = [response['hits']['hits'][0]] * topk * self.args.multiplier
#         candidates = [hit['_source']['message'] for hit in response['hits']['hits']]
#         query = 'test query'
#         return response, candidates, query, topk
#
#     def reorder(self, response, ranks):
#         hits = response['hits']['hits']
#         response['hits']['hits'] = [hit for _, hit in sorted(zip(ranks, hits))]
#
#         return response
#
#
# ES_EXAMPLE_DATA = {
#     "took": 5,
#     "timed_out": False,
#     "_shards": {
#         "total": 1,
#         "successful": 1,
#         "skipped": 0,
#         "failed": 0
#     },
#     "hits": {
#         "total": {
#             "value": 1,
#             "relation": "eq"
#         },
#         "max_score": 1.3862944,
#         "hits": [
#             {
#                 "_index": "twitter",
#                 "_type": "_doc",
#                 "_id": "0",
#                 "_score": 1.3862944,
#                 "_source": {
#                     "date": "2009-11-15T14:12:12",
#                     "likes": 0,
#                     "message": "trying out Elasticsearch",
#                     "user": "kimchy"
#                 }
#             }
#         ]
#     }
# }
