import unittest
from clients.es import ESClient
import aiohttp

from ..cli import set_parser

class TestEsClient(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--client', 'TestClient',
            '--model', 'TestModel',
        ])
        self.client = ESClient(args)


    def test_extract(self):
        field, value = ('description', 'test')
        async with aiohttp.request('GET', 'http://localhost:9200/test/_search?q={}:{}') as resp:
            assert resp.status == 200
            self.client.query()
            self.client.reorder()

    def test_reorder(self):
        pass