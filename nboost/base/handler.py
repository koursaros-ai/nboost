from httptools import HttpRequestParser, HttpResponseParser
from .protocol import BaseProtocol
from abc import abstractmethod
from typing import Union, Type
from .types import URL
from .exceptions import StatusRequest, UnknownRequest
import re

PARSERS_CLASSES = Union[Type[HttpRequestParser], Type[HttpResponseParser]]


class BaseHandler:
    def __init__(self, parser_cls: PARSERS_CLASSES):
        self.parser = parser_cls(self)
        self.is_done = False

    @abstractmethod
    def on_message_begin(self):
        pass

    def on_status(self, status: bytes):
        pass

    def on_url(self, url: bytes):
        pass

    @abstractmethod
    def on_header(self, name: bytes, value: bytes):
        pass

    @abstractmethod
    def on_headers_complete(self):
        pass

    @abstractmethod
    def on_body(self, body: bytes):
        pass

    def on_message_complete(self):
        self.is_done = True

    @abstractmethod
    def on_chunk_header(self):
        pass

    @abstractmethod
    def on_chunk_complete(self):
        pass

    def feed(self, data: bytes):
        self.parser.feed_data(data)


class RequestHandler(BaseHandler):
    def __init__(self, protocol: BaseProtocol):
        super().__init__(HttpRequestParser)
        self.protocol = protocol
        self.buffer = bytes()

    def on_message_begin(self):
        self.protocol.on_request_message_begin()

    def on_url(self, url: bytes):
        self.protocol.request.url = URL(url)
        self.protocol.request.method = self.parser.get_method().decode()

        path = self.protocol.request.url.path
        method = self.protocol.request.method
        search_pattern = self.protocol.SEARCH_PATH
        search_methods = self.protocol.SEARCH_METHODS
        status_pattern = self.protocol.STATUS_PATH
        status_methods = self.protocol.STATUS_METHODS

        if re.match(search_pattern, path) and method in search_methods:
            pass
        elif re.match(status_pattern, path) and method in status_methods:
            raise StatusRequest
        else:
            raise UnknownRequest

        self.protocol.on_request_url_and_method()

    def on_header(self, name: bytes, value: bytes):
        self.protocol.on_request_header(name.decode(), value.decode())

    def on_headers_complete(self):
        self.protocol.on_request_headers_complete()

    def on_body(self, body: bytes):
        self.protocol.on_request_body(body)

    def on_message_complete(self):
        self.protocol.on_request_message_complete()
        super().on_message_complete()

    def on_chunk_header(self):
        self.protocol.on_request_chunk_header()

    def on_chunk_complete(self):
        self.protocol.on_request_chunk_complete()

    def feed(self, data: bytes):
        self.buffer += data
        super().feed(data)


class ResponseHandler(BaseHandler):
    def __init__(self, protocol: BaseProtocol):
        super().__init__(HttpResponseParser)
        self.protocol = protocol

    def on_message_begin(self):
        self.protocol.on_response_message_begin()

    def on_status(self, status: bytes):
        self.protocol.on_response_status(self.parser.get_status_code())

    def on_header(self, name: bytes, value: bytes):
        self.protocol.on_response_header(name.decode(), value.decode())

    def on_headers_complete(self):
        self.protocol.on_response_headers_complete()

    def on_body(self, body: bytes):
        self.protocol.on_response_body(body)

    def on_message_complete(self):
        self.protocol.on_response_message_complete()
        super().on_message_complete()

    def on_chunk_header(self):
        self.protocol.on_response_chunk_header()

    def on_chunk_complete(self):
        self.protocol.on_response_chunk_complete()

