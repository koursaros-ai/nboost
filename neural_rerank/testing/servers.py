from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process, Event
from neural_rerank.base import set_logger
from typing import Tuple, Callable, Dict
from flask_compress import Compress
from flask import Flask, request
from .redict import RegexDict
from flask_cors import CORS
import functools
import logging
import time
import copy


# Subclass HTTPServer with some additional callbacks

# HTTP request handler


class TestHTTPHandler(BaseHTTPRequestHandler):
    server = None

    @classmethod
    def link(cls, server: 'TestHTTPServer'):
        cls.server = server

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    @classmethod
    def pre_start(cls):
        # print('Before calling socket.listen()')
        pass

    @classmethod
    def post_start(cls):
        # print('After calling socket.listen()')
        cls.server.is_ready.set()

    @classmethod
    def pre_stop(cls):
        # print('Before calling socket.close()')
        pass

    @classmethod
    def post_stop(cls):
        # print('After calling socket.close()')
        pass

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        try:
            self._set_headers()
            self.wfile.write(sorted(self.server.get_routes[:self.path:])[0][1]())
        except Exception as e:
            self.server.logger.error(repr(e), exc_info=True)
            self.wfile.write(repr(e).encode())

    def do_POST(self):
        try:
            # read the message and convert it into a python dictionary
            length = int(dict(self.headers._headers)['Content-Length'])
            message = self.rfile.read(length)

            # send the message back
            self._set_headers()
            self.wfile.write(sorted(self.server.post_routes[:self.path:])[0][1](message))
        except Exception as e:
            self.server.logger.error(repr(e), exc_info=True)
            self.wfile.write(repr(e).encode())


class TestHTTPServer(HTTPServer, Process):
    """ test http server that only supports get and post methods """
    handler = copy.deepcopy(TestHTTPHandler)

    def __init__(self, *args,
                 port: int = 8000,
                 get_routes: Dict[str, Callable] = {},
                 post_routes: Dict[str, Callable] = {},
                 **kwargs):
        self.port = port
        self.handler.link(self)
        self.get_routes = RegexDict(get_routes)
        self.post_routes = RegexDict(post_routes)
        self.is_ready = Event()
        self.logger = set_logger(self.__class__.__name__)
        HTTPServer.__init__(self, ('', port), self.handler)
        Process.__init__(self)

    def server_activate(self):
        self.RequestHandlerClass.pre_start()
        HTTPServer.server_activate(self)
        self.RequestHandlerClass.post_start()

    def server_close(self):
        self.RequestHandlerClass.pre_stop()
        HTTPServer.server_close(self)
        self.RequestHandlerClass.post_stop()

    def run(self):
        self.logger.info('SERVING on port %s' % self.port)
        self.serve_forever()

    def enter(self):
        self.start()
        self.is_ready.wait()

    def exit(self):
        self.server_close()
        self.terminate()
        self.join()
        self.is_ready.clear()


class TestFlaskServer(Process):
    """ A Flask server for testing purposes """

    def __init__(self,
                 *routes: Tuple[str, str, Callable],
                 host: str = '0.0.0.0',
                 port: int = 80):
        super().__init__()
        self.host = host
        self.port = port
        self.is_ready = Event()
        self.is_done = Event()
        werkzeug = logging.getLogger('werkzeug')
        werkzeug.setLevel(logging.ERROR)
        logger = set_logger(self.__class__.__name__)
        app = Flask(__name__)

        def add_url_rule(method: str, path: str, f: Callable):
            @functools.wraps(f)
            def log():
                try:
                    logger.info(request)
                    return f()
                except Exception as e:
                    logger.error('error when handling HTTP request', exc_info=True)
                    return dict(description=str(e), type=str(type(e).__name__))

            log.__name__ = str(hash(method + path))
            app.add_url_rule(path, None, log, methods=[method])
            return path, None, log

        for route in routes:
            add_url_rule(*route)

        CORS(app, origins='*')
        Compress().init_app(app)

        self.app = app
        self.logger = logger

    def run(self):
        self.is_ready.set()
        self.logger.critical('LISTENING: %s:%s' % (self.host, self.port))
        self.app.run(port=self.port, threaded=True, host=self.host)

    def enter(self):
        self.start()
        self.is_ready.wait()
        time.sleep(0.1)

    def exit(self):
        self.logger.critical('Stopping server...')
        self.terminate()
        self.join()
        time.sleep(1)
        self.is_done.set()
        self.is_ready.clear()

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

