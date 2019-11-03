import unittest
from ...cli import set_parser, set_logger
from ...proxies.rank import ESRankProxy
from elasticsearch import Elasticsearch
import requests
import csv
from ...paths import RESOURCES


class TestESProxy(unittest.TestCase):

    def setUp(self):
        self.logger = set_logger(self.__class__.__name__)
        self.es_index = 'test_index'
        self.es = Elasticsearch()
        self.es.indices.create(index=self.es_index, ignore=400)

        # id, query, product_title, product_description, median_relevance, relevance_variance
        with RESOURCES.joinpath('train.csv').open() as fh:
            sample_data = csv.reader(fh)
            self.logger.info('Dumping train.csv...')
            for row in list(sample_data)[:100]:
                self.es.index(index=self.es_index, id=row[0], body=dict(title=row[2], description=row[3]))

        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--model', 'TestModel',
            '--ext_port', '9200'
        ])
        self.proxy = ESRankProxy(**vars(args))
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        res = requests.get(self.proxy.url + '/%s/_search?q=description:test' % self.es_index)
        self.logger.info('%s:%s' % (res.status_code, res.content))
        # self.assertEqual(res.json()['msg'], 'server_response')

    def test_reorder(self):
        pass

    def tearDown(self):
        self.proxy.kill()
