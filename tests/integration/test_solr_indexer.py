from nboost.indexers.cli import main
import subprocess
import unittest
import requests
import time


class TestSolrIndexer(unittest.TestCase):
    def test_travel_tutorial(self):
        subprocess.call('docker pull solr:8.5.1', shell=True)
        subprocess.call('docker run -d -p 8983:8983 -t solr solr-precreate travel',
                        shell=True)

        #TODO: check if the core is ready by the api
        time.sleep(20.0)

        # dump es index
        main([
            '--verbose', 'True',
            '--port', '8983',
            '--file', 'travel.csv',
            '--index_name', 'travel',
            '--id_col',
            '--delim', ',',
            '--indexer', 'SolrIndexer'
        ])

        # search
        params = dict(size=2, q='_text_:hotels in vegas, baby')

        proxy_res = requests.get('http://localhost:8983/solr/travel/select', params=params)
        self.assertTrue(proxy_res.ok)
        exit(0)
