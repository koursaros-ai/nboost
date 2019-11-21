"""Base Protocol Class"""

from typing import List
from .types import Request, Response


class BaseProtocol:
    """The protocol class is the search engine api translation protocol. The
    protocol receives incoming http messages and parses them, executing the
    callbacks below as the appear.

    The goal of the protocol is to efficiently parse the request message and
    magnify it to increase the search results. Then, the protocol should parse
    the query and choices from the amplified search api results for the model
    to rank."""
    SEARCH_PATH = '/search'
    SEARCH_METHODS = ['GET']
    STATUS_PATH = '/nboost'
    STATUS_METHODS = ['GET']

    def __init__(self, multiplier: int = 10, field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.field = field
        self.topk = None  # type: int
        self.query = None  # type: str
        self.choices = []  # type: List[str]
        self.request = Request()
        self.response = Response()

    def on_request_message_begin(self):
        """Triggered on first bytes"""

    def on_request_url_and_method(self):
        """Request message attribute will have url and method at this point"""

    def on_request_header(self, name: str, value: str):
        """Alter request header as they come in if necessary"""
        self.request.headers[name] = value

    def on_request_headers_complete(self):
        """End of headers trigger"""

    def on_request_body(self, body: bytes):
        """Optionally access body stream"""
        self.request.body += body

    def on_request_message_complete(self):
        """Trigger when message finishes"""

    def on_request_chunk_header(self):
        """Chunked request header"""

    def on_request_chunk_complete(self):
        """Chunked request end"""

    def on_response_message_begin(self):
        """First magnified response bytes"""

    def on_response_status(self, status: int):
        """Status integer callback"""

    def on_response_header(self, name: str, value: str):
        """Alter response header as they come in if necessary"""
        self.response.headers[name] = value

    def on_response_headers_complete(self):
        """End of response headers trigger"""

    def on_response_body(self, body: bytes):
        """Optionally access body stream"""
        self.response.body += body

    def on_response_message_complete(self):
        """Trigger when message finishes"""

    def on_response_chunk_header(self):
        """Chunked response header"""

    def on_response_chunk_complete(self):
        """Chunked response end"""

    def on_rank(self, ranks: List[int]):
        """Reorder the response according to the model's ranks (argsorted)"""

    def on_error(self, exc: Exception):
        """Package the exception in case of service failure"""
