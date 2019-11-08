from neural_rerank.cli import create_proxy
from elasticsearch import Elasticsearch
from unittest.case import SkipTest
from tests.paths import RESOURCES
import unittest
import requests
import time
import csv


class TestESProxy(unittest.TestCase):
    def test_default_proxy(self):
        es = Elasticsearch()
        try:
            requests.get('http://localhost:9200/test_index/_stats')
        except requests.exceptions.ConnectionError:
            raise SkipTest('ES not available on port 9200')

        with RESOURCES.joinpath('train.csv').open() as fh:
            sample_data = csv.reader(fh)
            print('Dumping train.csv...')
            for row in list(sample_data)[:1000]:
                es.index(index='test_index', id=row[0], body=dict(
                    title=row[2], description=row[3]
                ))

        proxy = create_proxy([
            '--ext_port', '9200',
            '--field', 'description',
            '--multiplier', '2',
            '--verbose'
        ])
        proxy.enter()
        proxy.is_ready.wait()

        params = {'q': 'description:light'}
        proxy_res = requests.get('http://localhost:53001/test_index/_search', params=params)
        self.assertTrue(proxy_res.ok)
        total = proxy_res.json()['hits']['total']
        num_hits = len(proxy_res.json()['hits']['hits'])

        if isinstance(total, int):
            self.assertLess(num_hits, total)
        elif isinstance(total, dict):
            self.assertLess(num_hits, total['value'])
        else:
            self.skipTest('Expecting total to be int or dict but found type %s "%s"' % (type(total), total))

        proxy.exit()
        # time.sleep(30)
