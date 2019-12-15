from nboost.indexers.cli import main
import subprocess
import unittest
import requests


class TestESIndexer(unittest.TestCase):
    def test_travel_tutorial(self):
        subprocess.call('docker pull elasticsearch:7.4.2', shell=True)
        subprocess.call('docker run -d -p 9200:9200 -p 9300:9300 '
                        '-e "discovery.type=single-node" elasticsearch:7.4.2',
                        shell=True)

        # dump es index
        main([
            '--verbose',
            '--port', '9200',
            '--file', 'travel.csv',
            '--name', 'travel',
            '--id_col', '0',
            '--body_col', '1',
            '--delim', ','
        ])

        # search
        params = dict(size=2, q='passage:hotels in vegas, baby')

        proxy_res = requests.get('http://localhost:9200/travel/_search', params=params)
        self.assertTrue(proxy_res.ok)
