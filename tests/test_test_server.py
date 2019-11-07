import unittest
from multiprocessing import Process, Event
from flask import Flask, request
from flask_compress import Compress
from flask_cors import CORS
from neural_rerank.base import set_logger
import requests
from typing import Tuple, Callable
import json as JSON
import functools
import logging


class TestServer(Process):
    """ A server for testing purposes """

    def __init__(self,
                 *routes: Tuple[str, str, Callable],
                 host: str = '0.0.0.0',
                 port: int = 80):
        super().__init__()
        self.host = host
        self.port = port
        self.is_ready = Event()
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

    def exit(self):
        self.logger.critical('Stopping server...')
        self.terminate()
        self.join()

    def __enter__(self):
        self.start()
        self.is_ready.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()
        self.is_ready.clear()
        return self


class TestTestServer(unittest.TestCase):
    def setUp(self):
        def send_stuff():
            data = request.form if request.form else request.json
            return JSON.dumps(dict(got=data))

        self.server = TestServer(
            ('GET', '/get_stuff', lambda: JSON.dumps(dict(heres='some_stuff'))),
            ('GET', '/other_lambda', lambda: JSON.dumps(dict(youre='gluttonous'))),
            ('POST', '/send_stuff', send_stuff),
            port=56001
        )
        self.server.start()
        self.server.is_ready.wait()

    def test_get(self):
        res = requests.get('http://localhost:56001/get_stuff')
        print(res.content)
        self.assertTrue(res.ok)

        res = requests.get('http://localhost:56001/other_lambda')
        print(res.content)
        self.assertTrue(res.ok)

        res = requests.post('http://localhost:56001/send_stuff', data=dict(heres='an_avocado'))
        print(res.content)
        self.assertTrue(res.ok)

    def tearDown(self):
        self.server.stop()
