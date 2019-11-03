
from ...proxies.rank import ESProxy
from ..http import HTTPTestCase
from ...paths import RESOURCES
from elasticsearch import Elasticsearch
import csv


class TestESProxy(HTTPTestCase):

    def setUp(self):
        self.es_index = 'test_index'
        self.es = Elasticsearch()
        self.es.indices.create(index=self.es_index, ignore=400)

        # id, query, product_title, product_description, median_relevance, relevance_variance
        with RESOURCES.joinpath('train.csv').open() as fh:
            sample_data = csv.reader(fh)
            self.logger.info('Dumping train.csv...')
            for row in list(sample_data)[:100]:
                self.es.index(
                    index=self.es_index, id=row[0],
                    body=dict(title=row[2], description=row[3]))

        self.proxy = self.setUpServer(ESProxy, [
            '--model', 'TestModel',
            '--ext_port', '9200'
        ])

    def test_search_and_train(self):
        res = self.send(
            'GET',
            host=self.proxy.host,
            port=self.proxy.port,
            path='/%s/_search' % self.es_index,
            params={'q': 'description:test'}
        )

    def test_reorder(self):
        pass

    def tearDown(self):
        self.proxy.kill()
