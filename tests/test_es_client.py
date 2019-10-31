import unittest
from ..clients.es import ESClient
import aiohttp
from elasticsearch import Elasticsearch
import asyncio

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
        self.client = ESClient(args)
        self.es = Elasticsearch()
        self.es.indices.create(index='test', ignore=400)

        # id, query, product_title, product_description, median_relevance, relevance_variance
        with open(os.path.join(os.path.dirname(__file__), 'data', 'train.csv'), 'r') as file:
            sample_data = csv.reader(file)
            for row in list(sample_data)[:100]:
                # print('dumping line %s' % row[2])
                self.es.index(index="test",
                              id=row[0],
                              body={"title": row[2], "description": row[3]})

    async def test_extract(self):
        query = ('description', 'test')
        async with aiohttp.request('GET', 'http://localhost:9200/test/_search?q=%s:%s' % query) as resp:
            assert resp.status == 200
            print(await resp.json())
            # self.client.query()
            # self.client.reorder()

    def test_es(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete((self.test_extract()))

    def test_reorder(self):
        pass