from nboost.protocol import HttpProtocol
import unittest

REQUEST_PART_1 = b'GET /search?para=message HTTP/1.1\r\nContent-Length: 19'
REQUEST_PART_2 = b'\r\nTest-Header: Testing\r\n\r\n{"test": "request"}'

RESPONSE_PART_1 = b'HTTP/1.1 201 Created\r\nContent-Length: 20'
RESPONSE_PART_2 = b'\r\nTest-Header: 2\r\n\r\n{"test": "response"}'


class TestHttpProtocol(unittest.TestCase):

    def test_request(self):
        protocol = HttpProtocol()
        protocol.set_request_parser()
        request = {}
        protocol.set_request(request)
        protocol.add_url_hook(lambda url: self.assertEqual(url['path'], '/search'))
        protocol.add_data_hook(lambda data: self.assertIsInstance(data, bytes))

        protocol.feed(REQUEST_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(request['method'], 'GET')
        self.assertEqual(request['url']['query']['para'], 'message')

        protocol.feed(REQUEST_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(request['headers']['test-header'], 'Testing')
        self.assertEqual({'test': 'request'}, request['body'])

    def test_response(self):
        protocol = HttpProtocol()
        protocol.set_response_parser()
        response = {}
        protocol.set_response(response)

        protocol.feed(RESPONSE_PART_1)
        self.assertFalse(protocol._is_done)
        self.assertEqual(response['status'], 201)
        self.assertEqual(response['reason'], 'Created')

        protocol.feed(RESPONSE_PART_2)
        self.assertTrue(protocol._is_done)
        self.assertEqual(response['headers']['test-header'], '2')
        self.assertEqual({'test': 'response'}, response['body'])


