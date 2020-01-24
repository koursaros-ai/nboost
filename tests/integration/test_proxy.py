from nboost.proxy import Proxy
import subprocess
import unittest
import requests
from threading import Thread
from elasticsearch import Elasticsearch
import time
from pprint import pprint


class TestProxy(unittest.TestCase):
    def test_travel_tutorial(self):
        subprocess.call('docker pull elasticsearch:7.4.2', shell=True)
        subprocess.call('docker run -d -p 9200:9200 -p 9300:9300 '
                        '-e "discovery.type=single-node" elasticsearch:7.4.2',
                        shell=True)

        for _ in range(5):
            Elasticsearch().index(index='example', body={'field': 'value'})

        proxy = Proxy(
            model_dir='shuffle-model',
            model='ShuffleModelPlugin',
            uport=9200,
            debug=True,
            verbose=True, query_prep='lambda query: query.split(":")[-1]'
        )

        t = Thread(target=proxy.run)
        t.start()
        time.sleep(20)

        # search
        proxy_res = requests.get(
            'http://localhost:8000/example/_search',
            params={
                'q': 'field:value',
                'size': 3,
                'topn': 20
            }
        )

        self.assertTrue(proxy_res.ok)
        pprint(proxy_res.json())
        response = proxy_res.json()['nboost']
        self.assertEqual('value', response['query'])
        self.assertEqual(3, response['topk'])
        self.assertEqual(20, response['topn'])
        self.assertEqual(3, len(response['cvalues']))

        # fallback
        fallback_res = requests.get('http://localhost:8000/')
        self.assertTrue(fallback_res.ok)
        print(fallback_res.content.decode())

        # status
        status_res = requests.get('http://localhost:8000/nboost/status')
        self.assertTrue(status_res.ok)
        print(status_res.content.decode())

        # invalid host
        invalid_res = requests.get('http://localhost:8000/example/_search', params={'uport': 2000})
        print(invalid_res.content)
        self.assertFalse(invalid_res.ok)
