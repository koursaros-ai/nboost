from nboost.tutorial.cli import main
from nboost.cli import create_proxy
import subprocess
import unittest
import requests


class TestTravel(unittest.TestCase):
    def test_travel_tutorial(self):
        subprocess.call('docker pull elasticsearch:7.4.2',
                        shell=True)
        subprocess.call('docker run -d -p 9200:9200 -p 9300:9300 '
                        '-e "discovery.type=single-node" elasticsearch:7.4.2',
                        shell=True)

        proxy = create_proxy([
            '--uhost', 'localhost',
            '--uport', '9200',
            '--model', 'TestModel',
            '--field', 'passage',
            '--verbose'
        ])
        proxy.start()

        # dump es index
        main([
            'Travel',
            '--uhost', 'localhost',
            '--uport', '8000',
        ])

        # search
        params = dict(size=2, q='hotels in vegas, baby')

        proxy_res = requests.get('http://localhost:8000/travel/_search', params=params)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)
        self.assertIn('_nboost', proxy_res.json())

        proxy.close()
