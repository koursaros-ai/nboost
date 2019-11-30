from nboost.protocol import HttpProtocol
from nboost.types import Request, Response
import unittest

REQUEST_PART_1 = b'GET /search?para=message HTTP/1.1\r\nContent-Length: 9'
REQUEST_PART_2 = b'\r\nContent-Encoding: gzip\r\n\r\ntest body'

RESPONSE_PART_1 = b'HTTP/1.1 201 Created\r\nContent-Length: 4'
RESPONSE_PART_2 = b'\r\nTest-Header: 2\r\n\r\ntest'


class TestHttpProtocol(unittest.TestCase):

    def test_request(self):
        protocol = HttpProtocol()
        protocol.set_request_parser()
        request = Request()
        protocol.set_request(request)
        protocol.add_url_hook(lambda url: self.assertEqual(url.path, '/search'))
        protocol.add_data_hook(lambda data: self.assertIsInstance(data, bytes))

        protocol.feed(REQUEST_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.url.query['para'], 'message')

        protocol.feed(REQUEST_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(request.headers['content-encoding'], 'gzip')
        self.assertEqual(request.body, b'test body')

    def test_response(self):
        protocol = HttpProtocol()
        protocol.set_response_parser()
        response = Response()
        protocol.set_response(response)

        protocol.feed(RESPONSE_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(response.status, 201)
        self.assertEqual(response.reason, 'Created')

        protocol.feed(RESPONSE_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(response.headers['Test-Header'], '2')
        self.assertEqual(response.body, b'test')


