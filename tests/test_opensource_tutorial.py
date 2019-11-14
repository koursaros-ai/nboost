from nboost.cli import create_proxy
from tutorials.cli import main
import subprocess
import unittest
import requests


class TestProxy(unittest.TestCase):
    def test_opensource_tutorial(self):
        subprocess.call('docker pull elasticsearch:7.4.2',
                        shell=True)
        subprocess.call('docker run -d -p 9200:9200 -p 9300:9300 '
                        '-e "discovery.type=single-node" elasticsearch:7.4.2',
                        shell=True)

        proxy = create_proxy([
            '--ext_host', 'localhost',
            '--ext_port', '9200',
            '--model', 'TestModel',
            '--field', 'passage'
        ])
        proxy.start()

        # dump es index
        main([
            'opensource',
            '--host', 'localhost',
            '--port', '8000',
        ])

        # search
        params = dict(size=2, q='what is mozilla firefox')

        proxy_res = requests.get('http://localhost:8000/opensource/_search', params=params)
        print(proxy_res.content)
        self.assertTrue(proxy_res.ok)
        self.assertIn('_nboost', proxy_res.json())

        proxy.close()
