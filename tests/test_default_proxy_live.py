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

        queries = ['a', 'light', 'brown', 'dog']

        for q in queries:
            params = {'q': 'description:%s' % q}
            proxy_res = requests.get('http://localhost:53001/test_index/_search', params=params)
            self.assertTrue(proxy_res.ok)
            json = {'cid': proxy_res.json()['hits']['hits'][0]['cid']}
            train_res = requests.post('http://localhost:53001/train', json=json)
            self.assertTrue(train_res.ok)

        # time.sleep(30)
        proxy.exit()

