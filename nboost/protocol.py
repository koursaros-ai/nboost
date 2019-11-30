"""Base Protocol Class"""

from typing import List, Union, Callable
import socket
from httptools import HttpRequestParser, HttpResponseParser
from nboost.types import Request, Response, URL


class HttpProtocol:
    """The protocol class constructs the incoming request and response."""

    def __init__(self, sock: socket.socket = None):
        self._sock = sock
        self._bufsize = 2048
        self._data_hooks = []  # type: List[Callable]
        self._url_hooks = []  # type: List[Callable]
        self._parser = None  # type: Union[HttpRequestParser, HttpResponseParser]
        self._is_done = False
        self.msg = None  # type: Union[Request, Response]

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

    def set_request(self, request: Request):
        """Set new request"""
        self.msg = request

    def set_response(self, response: Response):
        """Set new response"""
        self.msg = response

    def feed(self, data: bytes):
        """feed data to the underlying parser"""
        for hook in self._data_hooks:
            hook(data)
        self._parser.feed_data(data)

    def recv(self):
        """Receive all incoming http data on a socket and execute hooks"""
        while not self._is_done:
            data = self._sock.recv(self._bufsize)
            self.feed(data)

    # HTTPTOOLS CALLBACK METHODS
    def on_message_begin(self):
        """Triggered on first bytes"""

    def on_status(self, status: bytes):
        """Status integer callback"""
        if self.msg is not None:
            self.msg.status = self._parser.get_status_code()

    def on_url(self, url: bytes):
        """Request message attribute will have url and method at this point"""
        url = URL(url)

        if self.msg is not None:
            self.msg.url = url
            self.msg.method = self._parser.get_method().decode()

        for hook in self._url_hooks:
            hook(url)

    def on_header(self, name: bytes, value: bytes):
        """Alter request header as they come in if necessary"""
        if self.msg is not None:
            self.msg.headers[name.decode()] = value.decode()

    def on_headers_complete(self):
        """End of headers trigger"""

    def on_body(self, body: bytes):
        """Optionally access body stream"""
        if self.msg is not None:
            self.msg.body += body

    def on_message_complete(self):
        """Trigger when message finishes"""
        self._is_done = True

    def on_chunk_header(self):
        """Chunked message header"""

    def on_chunk_complete(self):
        """Chunked response end"""
