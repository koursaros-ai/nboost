"""Base types for NBoost"""

from http.client import responses
from typing import Dict, Union
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
from requests.structures import CaseInsensitiveDict as CID
import gzip

HTTP1_1 = 'HTTP/1.1'


class URL:
    """scheme://netloc/path;params?query#fragment"""
    __slots__ = ['scheme', 'netloc', 'path', 'params', 'query',
                 'fragment', 'raw']

    def __init__(self, url: bytes):
        self.raw = url  # useful for debugging
        url = urlparse(url.decode())
        self.scheme = url.scheme  # type: str
        self.netloc = url.netloc  # type: str
        self.path = url.path  # type: str
        self.params = url.params  # type: str
        qsl = parse_qsl(url.query, keep_blank_values=True)
        self.query = dict(qsl) if url.query else {}  # type: Dict[str, str]
        self.fragment = url.fragment  # type: str

    def __repr__(self):
        return urlunparse((self.scheme, self.netloc, self.path, self.params,
                           urlencode(self.query), self.fragment))


class Request:
    """The object that the server must pack all requests into. This is
    necessary to support multiple search apis."""
    __slots__ = ['method', 'url', 'version', 'headers', 'body']

    def __init__(self):
        self.version = HTTP1_1
        self.headers = CID()
        self.url = None  # type: URL
        self.body = bytes()
        self.method = str()

    def __repr__(self):
        return '<Request %s %s>' % (self.url, self.method)

    def decode(self):
        """decode request"""
        decode_msg(self)

    def encode(self):
        """encode request"""
        encode_msg(self)

    def prepare(self) -> bytes:
        """Prepare the request for socket transmission"""
        self.headers['content-length'] = str(len(self.body))
        headers = ''.join(
            '\r\n%s: %s' % (k, v) for k, v in self.headers.items())
        return '{method} {url} {version}{headers}\r\n\r\n'.format(
            method=self.method, url=str(self.url), version=self.version,
            headers=headers
        ).encode() + self.body


class Response:
    """The object that each response must be packed into before sending. Same
    reason as the Request object. """
    __slots__ = ['version', 'status', 'headers', 'body']

    def __init__(self):
        self.version = HTTP1_1
        self.status = 200
        self.headers = CID()
        self.body = bytes()

    def __repr__(self):
        return '<Response %s %s>' % (self.status, self.reason)

    @property
    def reason(self):
        """Third argument in response status line"""
        return responses[self.status]

    def decode(self):
        """decode response"""
        decode_msg(self)

    def encode(self):
        """encode response"""
        encode_msg(self)

    def prepare(self) -> bytes:
        """Prepare the response for socket transmission"""
        self.headers['content-length'] = str(len(self.body))
        return '{version} {status} {reason}{headers}\r\n\r\n'.format(
            version=self.version, status=self.status, reason=self.reason,
            headers=''.join(
                '\r\n%s: %s' % (k, v) for k, v in self.headers.items())
        ).encode() + self.body


def decode_msg(msg: Union[Request, Response]):
    """Decode the message's body"""
    if msg.headers.get('content-encoding', '') == 'gzip':
        msg.body = gzip.decompress(msg.body)


def encode_msg(msg: Union[Request, Response]):
    """Encode the message's body"""
    if msg.headers.get('content-encoding', '') == 'gzip':
        msg.body = gzip.compress(msg.body)
