import unittest
from ..proxies.es import ESProxy
from ..models.test import TestModel
import aiohttp
from elasticsearch import Elasticsearch
import asyncio
from aiohttp import web
import requests

import os
import csv
from ..cli import set_parser


class TestESProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        self.args = parser.parse_args([
            '--verbose',
            '--host', 'localhost',
            '--port', '9200',
        ])
        self.es = Elasticsearch()
        self.es.indices.create(index='test', ignore=400)
        self.model = TestModel(self.args)
        self.url = 'http://%s:%s/' % (self.args.proxy_host, self.args.proxy_port)
        self.es_index = 'test'

        # id, query, product_title, product_description, median_relevance, relevance_variance
        with open(os.path.join(os.path.dirname(__file__), 'data', 'train.csv'), 'r') as file:
            sample_data = csv.reader(file)
            for row in list(sample_data)[:100]:
                # print('dumping line %s' % row[2])
                self.es.index(index=self.es_index,
                              id=row[0],
                              body={"title": row[2], "description": row[3]})

    def test_search(self):
        client = ESProxy(self.args)
        client.start()
        client.is_ready.wait()
        res = requests.get(self.url + self.es_index + '/_search?q=description:test')
        print(res)
        assert res.ok

    def test_reorder(self):
        pass

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