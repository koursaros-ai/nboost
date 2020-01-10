"""Base Protocol Class"""

from typing import List, Union, Callable
import socket
import gzip
from httptools import HttpRequestParser, HttpResponseParser, HttpParserError
from nboost.helpers import parse_url, load_json

PARSER_TYPE = Union[HttpRequestParser, HttpResponseParser]


class HttpProtocol:
    """The protocol class constructs the incoming request and response."""

    def __init__(self, bufsize: int = 2048):
        self._bufsize = bufsize
        self._data_hooks = []  # type: List[Callable]
        self._url_hooks = []  # type: List[Callable]
        self._parser = None  # type: PARSER_TYPE
        self._is_done = False
        self._body = bytes()
        self.msg = None

    def add_url_hook(self, func: Callable):
        """Add hook to be executed during on_url()"""
        self._url_hooks.append(func)

    def add_data_hook(self, func: Callable):
        """Add hook to be executed during recv()"""
        self._data_hooks.append(func)

    def set_bufsize(self, bufsize: int):
        """Set the bytes size to read from the socket"""
        self._bufsize = bufsize

    def set_request_parser(self):
        """Set a new request parser with self as callback"""
        self._parser = HttpRequestParser(self)

    def set_response_parser(self):
        """Set a new response parser with self as callback"""
        self._parser = HttpResponseParser(self)

    def set_request(self, request: dict):
        """Set new request"""
        self.msg = request
        self.set_request_parser()

    def set_response(self, response: dict):
        """Set new response"""
        self.msg = response
        self.set_response_parser()

    def feed(self, data: bytes):
        """feed data to the underlying parser. Exceptions raised in the http
        parser must be reraised from __context__ because they are caught by
        the MagicStack implementation."""
        for hook in self._data_hooks:
            hook(data)

        try:
            self._parser.feed_data(data)
        except HttpParserError as exc:
            raise exc.__context__ if exc.__context__ else exc

    def recv(self, sock: socket.socket):
        """Receive all incoming http data on a socket and execute hooks"""
        while not self._is_done:
            data = sock.recv(self._bufsize)
            self.feed(data)

    # HTTPTOOLS CALLBACK METHODS
    def on_message_begin(self):
        """Triggered on first bytes"""

    def on_status(self, status: bytes):
        """Status integer callback"""
        if self.msg is not None:
            self.msg['status'] = self._parser.get_status_code()
            self.msg['reason'] = status.decode()

    def on_url(self, url: bytes):
        """Request message attribute will have url and method at this point"""
        url = parse_url(url)

        if self.msg is not None:
            self.msg['url'] = url
            self.msg['method'] = self._parser.get_method().decode()

        for hook in self._url_hooks:
            hook(url)

    def on_header(self, name: bytes, value: bytes):
        """Alter request header as they come in if necessary"""
        if self.msg is not None:
            self.msg['headers'][name.decode().lower()] = value.decode()

    def on_headers_complete(self):
        """End of headers trigger"""

    def on_body(self, body: bytes):
        """Optionally access body stream"""
        self._body += body

    def on_message_complete(self):
        """Trigger when message finishes"""

        if self.msg is not None:
            self.msg['version'] = 'HTTP/' + self._parser.get_http_version()

            if self.msg['headers'].get('content-encoding', '') == 'gzip':
                self._body = gzip.decompress(self._body)

            self.msg['body'].update(load_json(self._body))

        self._is_done = True

    def on_chunk_header(self):
        """Chunked message header"""

    def on_chunk_complete(self):
        """Chunked response end"""
