from nboost.server import AioHttpServer
from nboost.base.types import *
import json as JSON
import requests
import unittest


class TestAioHttpServer(unittest.TestCase):
    def test_aiohttp_server(self):

        server = AioHttpServer(port=6000, ext_port=5900, verbose=True)

        async def get_stuff(req):
            return Response({}, JSON.dumps(dict(heres='stuff')).encode(), 200)

        async def post_stuff(req):
            return Response({}, b'I got %s' % req.body, 200)

        server.create_app({
            Route.SEARCH: ({'/get_stuff': ['GET']}, get_stuff),
            Route.TRAIN: ({'/send_stuff': ['POST']}, post_stuff),
        })

        server.start()
        server.is_ready.wait()
        # time.sleep(1)
        self.assertTrue(server.is_ready.is_set())

        res = requests.get('http://localhost:6000/get_stuff')
        print(res.content)
        self.assertTrue(res.ok)

        res = requests.post('http://localhost:6000/send_stuff',
                            json=dict(sent='an_avocado'))
        print(res.content)
        self.assertTrue(res.ok)

        server.stop()
        server.join()
