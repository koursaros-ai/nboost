from nboost.server.loop import LoopServer
from nboost.base.types import *
import requests
import unittest


class TestLoopServer(unittest.TestCase):
    def test_loop_server(self):
        server = LoopServer(port=6000, ext_port=5900, verbose=True)

        async def get_stuff(req):
            response = Response()
            response.json = dict(heres='stuff')
            return response

        async def send_stuff(req):
            return Response(body=b'I got ' + req.body)

        server.create_app([
            ('/get_stuff', ['GET'], get_stuff),
            ('/send_stuff', ['POST'], send_stuff),
        ], not_found_handler=lambda x: x)

        server.start()
        server.is_ready.wait()
        self.assertTrue(server.is_ready.is_set())

        res = requests.get('http://localhost:6000/get_stuff')
        self.assertTrue(res.ok)

        res = requests.post('http://localhost:6000/send_stuff', data=b'an avocado')
        self.assertTrue(res.ok)
        print(res.content)

        server.stop()
        server.join()
