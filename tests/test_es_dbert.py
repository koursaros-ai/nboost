from neural_rerank.cli import create_proxy
from neural_rerank.clients import ESClient
from neural_rerank.models import DBERTRank
from tests.helpers import check_es_index
import requests
import unittest
import multiprocessing as mp

import time

ES_HOST = '127.0.01'
ES_PORT = '9200'
ES_INDEX = 'test_index'


class TestESDBERTProxy(unittest.TestCase):

    def setUp(self):
        self.proxy = create_proxy(model_cls=DBERTRank, client_cls=ESClient, argv=[
            '--ext_host', ES_HOST,
            '--ext_port', ES_PORT,
            '--field', 'description',
            '--multiplier', '2',
            '--verbose'
        ])
        mp.set_start_method('spawn')
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_es_proxy(self):

        check_es_index(
            self.proxy.client.ext_host,
            self.proxy.client.ext_port,
            ES_INDEX
        )

        proxy_res = requests.get(
                'http://%s:%s/%s/_search' % (self.proxy.host, self.proxy.port, ES_INDEX),
                params={'q': 'description:light'}
            )

        self.assertTrue(proxy_res.ok)
        total = proxy_res.json()['hits']['total']
        num_hits = len(proxy_res.json()['hits']['hits'])

        if isinstance(total, int):
            self.assertLess(num_hits, total)
        elif isinstance(total, dict):
            self.assertLess(num_hits, total['value'])
        else:
            self.skipTest('Expecting total to be int or dict but found type %s "%s"' % (type(total), total))

        # time.sleep(30)

    def tearDown(self):
        self.proxy.close()
