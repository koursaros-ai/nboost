from neural_rerank.proxies.rank import ESProxy
from ..http import HTTPTestCase
from paths import RESOURCES
from elasticsearch import Elasticsearch
import csv
import time
import requests

ES_PORT = 9200
INDEX_SIZE = 1000


class TestESProxy(HTTPTestCase):

    def setUp(self):
        self.es_index = 'test_index'
        self.proxy = self.setUpServer(ESProxy, [
            '--model', 'TestModel',
            '--ext_port', str(ES_PORT),
            '--field', 'description',
            '--multiplier', '2'
        ])

        self.es = Elasticsearch()

    def test_es_proxy(self):

        try:
            res = self.send('GET', port=ES_PORT, path='/test_index/_stats')
        except requests.exceptions.ConnectionError:
            self.logger.error('ES not available on port %s' % ES_PORT)
            self.skipTest('')
            raise SystemExit

        if res.json()['_all']['primaries']['docs']['count'] < INDEX_SIZE:
            self.es.indices.create(index=self.es_index, ignore=400)

            # id, query, product_title, product_description, median_relevance, relevance_variance
            with RESOURCES.joinpath('train.csv').open() as fh:
                sample_data = csv.reader(fh)
                self.logger.info('Dumping train.csv...')
                for row in list(sample_data)[:INDEX_SIZE]:
                    self.es.index(
                        index=self.es_index, id=row[0],
                        body=dict(title=row[2], description=row[3]))

        path = '/%s/_search' % self.es_index
        params = {'q': 'description:light'}
        res = self.get_from(self.proxy, path=path, params=params)

        self.assertLess(
            len(res.json()['hits']['hits']),
            res.json()['hits']['total']
        )

        status = self.get_from(self.proxy, path='/status')
        # time.sleep(30)

    def tearDown(self):
        self.proxy.kill()
