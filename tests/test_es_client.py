import unittest
from ..clients.es import ESClient
from ..models.test import TestModel
import aiohttp
from elasticsearch import Elasticsearch
import asyncio
from aiohttp import web

import os
import csv
from ..cli import set_parser

class TestESClient(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel',
        ])
        self.client = ESClient('localhost', 9200, args)
        self.es = Elasticsearch()
        self.es.indices.create(index='test', ignore=400)
        self.model = TestModel(args)

        # id, query, product_title, product_description, median_relevance, relevance_variance
        with open(os.path.join(os.path.dirname(__file__), 'data', 'train.csv'), 'r') as file:
            sample_data = csv.reader(file)
            for row in list(sample_data)[:100]:
                # print('dumping line %s' % row[2])
                self.es.index(index="test",
                              id=row[0],
                              body={"title": row[2], "description": row[3]})

    async def test_extract(self):
        request = web.BaseRequest()
        (resp, query, candidates, topk) = self.client.query(request)
        self.model.rank(query[1], candidates)

    def test_es(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete((self.test_extract()))

    def test_reorder(self):
        pass