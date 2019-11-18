from urllib.parse import parse_qsl
from httptools import parse_url
from ...base.types import *
from typing import Union

GZIP = b'gzip'
CRLF = b'\r\n'
COLON = b': '
SPACE = b' '
QMARK = b'?'
WILDCARD = b'*'
ENCODING = b'Content-Encoding'
ACCEPTS = b'Accept-Encoding'
CORS = b'Access-Control-Allow-Origin'
LENGTH = b'Content-Length'
HTTP1_1 = b'HTTP/1.1'


class HttpProtocol:
    def __init__(self, msg: Union[Request, Response]):
        self.msg = msg
        self.complete = False

    def on_message_begin(self):
        pass

    def on_url(self, url: bytes):
        url = parse_url(url)
        self.msg.path = url.path.decode()
        query = url.query
        self.msg.params = dict(parse_qsl(query.decode())) if query else {}

    def on_header(self, name: bytes, value: bytes):
        self.msg.headers[name.decode()] = value.decode()

    def on_headers_complete(self):
        pass

    def on_body(self, body: bytes):
        self.msg.body += body

    def on_message_complete(self):
        self.complete = True

    def on_chunk_header(self):
        pass

    def on_chunk_complete(self):
        pass

    def on_status(self, status: bytes):
        pass


def prepare_request(request: Request) -> bytes:
    return '{method} {url} {version}{headers}\r\n\r\n'.format(
        method=request.method,
        url=request.url,
        version=request.version,
        headers=''.join('\r\n%s: %s'%(k,v)for k,v in request.headers.items())
    ).encode() + request.body


def prepare_response(response: Response) -> bytes:
    return '{version} {status} {reason}{headers}\r\n\r\n'.format(
        version=response.version,
        status=response.status,
        reason=response.reason,
        headers=''.join('\r\n%s: %s'%(k,v)for k,v in response.headers.items())
    ).encode() + response.body
