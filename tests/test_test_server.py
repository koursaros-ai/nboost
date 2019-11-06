
import unittest
from multiprocessing import Process, Event
from flask import Flask, request
# from flask_compress import Compress
from flask_cors import CORS
from flask_json import FlaskJSON, as_json, JsonError
from neural_rerank.base import set_logger
import requests

HOST = '0.0.0.0'
PORT = 55001


class TestServer(Process):
    """ A server for testing purposes """
    def __init__(self):
        super().__init__()
        self.is_ready = Event()

    def create_flask_app(self):
        app = Flask(__name__)
        logger = set_logger(self.__class__.__name__)

        @app.route('/get_stuff', methods=['GET'])
        @as_json
        def get_stuff():
            return {'heres': 'some_stuff'}

        @app.route('/send_stuff', methods=['POST'])
        @as_json
        def send_stuff():
            data = request.form if request.form else request.json
            try:
                logger.info('new request from %s' % request.remote_addr)
                logger.debug(data)
                return {'got': 'your_stuff'}

            except Exception as e:
                logger.error('error when handling HTTP request', exc_info=True)
                raise JsonError(description=str(e), type=str(type(e).__name__))

        CORS(app, origins='*')
        FlaskJSON(app)
        # Compress().init_app(app)
        return app

    def run(self):
        app = self.create_flask_app()
        self.is_ready.set()
        app.run(port=PORT, threaded=True, host=HOST)


class TestTestServer(unittest.TestCase):
    def setUp(self):
        self.server = TestServer()
        self.server.start()
        self.server.is_ready.wait()

    def test_get(self):
        import time
        time.sleep(1)
        # res = request.get('http://%s:%s/get_stuff' % (HOST, PORT))
        # print(res.content)
        # self.assertTrue(res.ok)
        #
        # res = request.post('http://%s:%s/send_stuff' % (HOST, PORT))
        # print(res.content)
        # self.assertTrue(res.ok)

    def tearDown(self):
        self.server.terminate()
        self.server.join()

