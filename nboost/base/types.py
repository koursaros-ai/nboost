from typing import Dict
from enum import Enum
from requests.structures import CaseInsensitiveDict


class Route(Enum):
    """Used as keys for the route dictionary created by the proxy."""
    SEARCH = 0
    TRAIN = 1
    STATUS = 2
    NOT_FOUND = 3
    ERROR = 4


class Request:
    """The object that the server/codex must pack all requests into. This is
    necessary to support multiple search apis."""
    __slots__ = ['method', 'path', 'params', 'version', 'headers', 'body']

    def __init__(self,
                 method: bytes,
                 path: bytes,
                 params: Dict[bytes, bytes],
                 version: bytes,
                 headers: Dict[bytes, bytes],
                 body: bytes):
        self.method = method
        self.path = path
        self.params = params
        self.version = version
        self.headers = CaseInsensitiveDict(headers)
        self.body = body


class Response:
    """The object that each response must be packed into before sending. Same
    reason as the Request object. """
    __slots__ = ['version', 'status', 'phrase', 'headers', 'body']

    def __init__(self,
                 version: bytes,
                 status: int,
                 headers: Dict[bytes, bytes],
                 body: bytes):
        self.version = version
        self.status = status
        self.headers = CaseInsensitiveDict(headers)
        self.body = body


class Qid(bytes):
    """An id for a query"""


class Query:
    """A query from the client """
    __slots__ = ['body', 'ident']

    def __init__(self, body: bytes, ident: Qid = None):
        self.body = body
        self.ident = ident


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
        self.body = body
        self.ident = ident
        self.rank = rank
        self.label = label


class Topk(int):
    """Number of results the client requested"""
