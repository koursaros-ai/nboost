from neural_rerank.testing import TestFlaskServer
import json as JSON
import requests
import unittest


class TestTestServer(unittest.TestCase):
    def test_test_server(self):

        server = TestFlaskServer(
            ('GET', '/get_stuff', lambda: JSON.dumps(dict(heres='some_stuff'))),
            ('GET', '/other_lambda', lambda: JSON.dumps(dict(youre='gluttonous'))),
            ('POST', '/send_stuff', lambda: JSON.dumps(dict(got='data'))),
            port=6000
        )

        server.enter()
        # time.sleep(1)
        self.assertTrue(server.is_ready.is_set())

        res = requests.get('http://localhost:6000/get_stuff')
        print(res.content)
        self.assertTrue(res.ok)

        res = requests.get('http://localhost:6000/other_lambda')
        print(res.content)
        self.assertTrue(res.ok)

        res = requests.post('http://localhost:6000/send_stuff', data=dict(heres='an_avocado'))
        print(res.content)
        self.assertTrue(res.ok)

        server.exit()
