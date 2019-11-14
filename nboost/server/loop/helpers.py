from urllib.parse import urlparse, parse_qsl, urlencode
from http.client import responses
from typing import Tuple, List
from ...base import *
import gzip

GZIP = b'gzip'
CRLF = b'\r\n'
COLON = b': '
SPACE = b' '
QMARK = b'?'
WILDCARD = b'*'
ENCODING = b'content-encoding'
CORS = b'access-control-allow-origin'
LENGTH = b'content-length'


def parse_http_message(b: bytes) -> Tuple[bytes, dict, bytes]:
    """Returns the first line, headers, and body"""
    idx = b.find(CRLF * 2)
    body = b[idx + len(CRLF * 2):]
    prebody = b[:idx].split(CRLF)
    headers = list(reversed(prebody))
    first_line = headers.pop()
    headers = dict([h.split(COLON) for h in headers])
    return first_line, headers, body


def format_http_message(first_line: bytes, headers: dict, body: bytes) -> bytes:
    """Formats http message into bytes. Field names are lowercased."""
    headers = CRLF.join([k.lower()+COLON+v for k, v in headers.items()])
    return first_line + CRLF + headers + CRLF * 2 + body


# REQUESTS

def parse_start_line(start_line: bytes) -> List[bytes]:
    """Parse start line of http request to method, target, version"""
    return start_line.split()


def format_start_line(method: bytes, path: bytes, params: dict, version: bytes) -> bytes:
    """Format start line for http requests"""
    target = path
    if params:
        target += QMARK + urlencode(params).encode()
    return method + SPACE + target + SPACE + version


def bytes_to_request(b: bytes) -> Request:
    start_line, headers, body = parse_http_message(b)
    method, target, version = parse_start_line(start_line)
    url = urlparse(target)
    path = url.path
    params = dict(parse_qsl(url.query))

    return Request(method, path, params, version, headers, body)


def request_to_bytes(req: Request) -> bytes:
    start_line = format_start_line(req.method, req.path, req.params, req.version)
    return format_http_message(start_line, req.headers, req.body)


# RESPONSES

def parse_status_line(status_line: bytes) -> Tuple[bytes, int]:
    """Parse the status line of an http response to version and status"""
    status_line = status_line.split()
    return status_line[0], int(status_line[1])


def format_status_line(version: bytes, status: int):
    return version + SPACE + str(status).encode() + SPACE + responses[status].encode()


def bytes_to_response(b: bytes) -> Response:
    first_line, headers, body = parse_http_message(b)
    version, status = parse_status_line(first_line)

    if headers.get(ENCODING, None) == GZIP:
        body = gzip.decompress(body)

    return Response(version, status, headers, body)


def response_to_bytes(res: Response) -> bytes:
    status_line = format_status_line(res.version, res.status)
    body = res.body

    res.headers[CORS] = WILDCARD
    res.headers[LENGTH] = str(len(body)).encode()

    if res.headers.get(ENCODING, None) == GZIP:
        body = gzip.compress(body)

    return format_http_message(status_line, res.headers, body)