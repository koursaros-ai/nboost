from nboost.protocol import HttpProtocol
from nboost.session import Session
import unittest

REQUEST_PART_1 = b'GET /search?para=message HTTP/1.1\r\nContent-Length: 19'
REQUEST_PART_2 = b'\r\nTest-Header: Testing\r\n\r\n{"test": "request"}'

RESPONSE_PART_1 = b'HTTP/1.1 201 Created\r\nContent-Length: 20'
RESPONSE_PART_2 = b'\r\nTest-Header: 2\r\n\r\n{"test": "response"}'


class TestHttpProtocol(unittest.TestCase):

    def test_request(self):
        protocol = HttpProtocol()
        protocol.set_request_parser()
        session = Session()
        protocol.set_request(session.request)
        protocol.add_url_hook(lambda url: self.assertEqual(url['path'], '/search'))
        protocol.add_data_hook(lambda data: self.assertIsInstance(data, bytes))

        protocol.feed(REQUEST_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(session.request['method'], 'GET')
        self.assertEqual(session.request['url']['query']['para'], 'message')

        protocol.feed(REQUEST_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(session.request['headers']['test-header'], 'Testing')
        self.assertEqual({'test': 'request'}, session.request['body'])

    def test_response(self):
        protocol = HttpProtocol()
        session  = Session()
        protocol.set_response_parser()
        protocol.set_response(session.response)

        protocol.feed(RESPONSE_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(session.response['status'], 201)
        self.assertEqual(session.response['reason'], 'Created')

        protocol.feed(RESPONSE_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(session.response['headers']['test-header'], '2')
        self.assertEqual({'nboost': {}, 'test': 'response'}, session.response['body'])


