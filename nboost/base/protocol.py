from .types import Request, Response, URL
from typing import List


class BaseProtocol:
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
        pass

    def on_request_url_and_method(self):
        pass

    def on_request_header(self, name: str, value: str):
        self.request.headers[name] = value

    def on_request_headers_complete(self):
        pass

    def on_request_body(self, body: bytes):
        self.request.body += body

    def on_request_message_complete(self):
        pass

    def on_request_chunk_header(self):
        pass

    def on_request_chunk_complete(self):
        pass

    def on_response_message_begin(self):
        pass

    def on_response_status(self, status: int):
        pass

    def on_response_url_and_method(self, url: URL, method: str):
        pass

    def on_response_header(self, name: str, value: str):
        self.response.headers[name] = value

    def on_response_headers_complete(self):
        pass

    def on_response_body(self, body: bytes):
        self.response.body += body

    def on_response_message_complete(self):
        pass

    def on_response_chunk_header(self):
        pass

    def on_response_chunk_complete(self):
        pass

    def on_response_prepare(self):
        pass

    def on_rank(self, ranks: List[int]):
        pass

    def on_error(self, e: Exception):
        raise NotImplementedError

