from typing import Dict
from enum import Enum
from requests.structures import CaseInsensitiveDict as CID
from urllib.parse import urlencode
from http.client import responses
import json as JSON
import gzip

HTTP1_1 = 'HTTP/1.1'


class Route(Enum):
    """Used as keys for the route dictionary created by the proxy."""
    SEARCH = 0
    TRAIN = 1
    STATUS = 2
    NOT_FOUND = 3
    ERROR = 4


class HttpMessage:
    def __init__(self,
                 version: str = HTTP1_1,
                 headers: Dict[str, str] = None,
                 body: bytes = bytes()):
        self.version = version
        self.headers = CID(headers)
        self.body = bytes(body)

    @property
    def json(self) -> dict:
        return JSON.loads(self.body)

    @json.setter
    def json(self, value: dict):
        self.body = JSON.dumps(value).encode()

    @property
    def is_gzip(self) -> bool:
        return self.headers.get('content-encoding', None) == 'gzip'

    def gzip(self):
        self.body = gzip.compress(self.body)

    def ungzip(self):
        self.body = gzip.decompress(self.body)


class Request(HttpMessage):
    """The object that the server/codex must pack all requests into. This is
    necessary to support multiple search apis."""
    __slots__ = ['method', 'path', 'params', 'version', 'headers', 'body']

    def __init__(self,
                 version: str = HTTP1_1,
                 headers: Dict[str, str] = None,
                 body: bytes = bytes(),
                 method: str = None,
                 path: str = None,
                 params: Dict[str, str] = None):
        super().__init__(version, headers, body)
        self.method = method
        self.path = path
        self.params = dict(params) if params else {}

    def __repr__(self):
        return '<Request %s %s>' % (self.path, self.method)

    @property
    def url(self) -> str:
        return self.path + '?' + urlencode(self.params) if self.params else ''


class Response(HttpMessage):
    """The object that each response must be packed into before sending. Same
    reason as the Request object. """
    __slots__ = ['version', 'status', 'headers', 'body']

    def __init__(self,
                 version: str = HTTP1_1,
                 status: int = 200,
                 headers: Dict[str, str] = None,
                 body: bytes = bytes()):
        super().__init__(version, headers, body)
        self.status = int(status)

    def __repr__(self):
        return '<Response %s %s>' % (self.status, self.reason)

    @property
    def reason(self):
        return responses[self.status]


class Qid(bytes):
    """An id for a query"""


class Query:
    """A query from the client """
    __slots__ = ['body', 'ident']

    def __init__(self, body: bytes, ident: Qid = Qid()):
        self.body = bytes(body)
        self.ident = Qid(ident)


class Cid(bytes):
    """An id for a choice"""


class Choice:
    """A list of candidates returned by the search api. Each one may have
     a label which is a list of floats representing the forward pass value for
     a respective list of choice. Also a rank, representing it's ranks for a
    respective list of choices."""
    __slots__ = ['body', 'ident', 'rank', 'label']

    def __init__(self,
                 body: bytes,
                 ident: Cid = None,
                 rank: int = None,
                 label: float = None):
        self.body = bytes(body) if body else bytes()
        self.ident = None if ident is None else Cid(ident)
        self.rank = None if rank is None else int(rank)
        self.label = None if label is None else float(label)


class Topk(int):
    """Number of results the client requested"""
