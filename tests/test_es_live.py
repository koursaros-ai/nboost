from neural_rerank.proxies import ESProxy
from neural_rerank.cli import set_parser
from tests.paths import RESOURCES
from elasticsearch import Elasticsearch
import csv
import unittest
import time
import requests

ES_HOST = '127.0.01'
ES_PORT = '9200'
INDEX_SIZE = 1000
ES_INDEX = 'test_index'


class TestESProxy(unittest.TestCase):

    def setUp(self):
        self.es_index = 'test_index'
        parser = set_parser()
        self.proxy = ESProxy(**vars(parser.parse_args([
            '--ext_host', ES_HOST,
            '--ext_port', ES_PORT,
            '--field', 'description',
            '--multiplier', '2',
            '--verbose'
        ])))

        self.es = Elasticsearch()
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_es_proxy(self):

        try:
            es_res = requests.get(
                'http://%s:%s/%s/_stats' % (self.proxy.ext_host, self.proxy.ext_port, ES_INDEX)
            )
        except requests.exceptions.ConnectionError:
            self.skipTest('ES not available on port %s' % ES_PORT)
            raise SystemExit

        if es_res.json()['_all']['primaries']['docs']['count'] < INDEX_SIZE:
            self.es.indices.create(index=ES_INDEX, ignore=400)

            # id, query, product_title, product_description, median_relevance, relevance_variance
            with RESOURCES.joinpath('train.csv').open() as fh:
                sample_data = csv.reader(fh)
                print('Dumping train.csv...')
                for row in list(sample_data)[:INDEX_SIZE]:
                    self.es.index(
                        index=ES_INDEX, id=row[0],
                        body=dict(title=row[2], description=row[3]))

        proxy_res = requests.get(
                'http://%s:%s/%s/_search' % (self.proxy.host, self.proxy.port, ES_INDEX),
                params={'q': 'description:light'}
            )
        self.assertTrue(proxy_res.ok)

        self.assertLess(
            len(proxy_res.json()['hits']['hits']),
            proxy_res.json()['hits']['total']
        )

        # time.sleep(30)

    def tearDown(self):
        self.proxy.kill()
