import unittest
import requests
from ..cli import set_logger, format_response, set_parser
import sys
from typing import List
from ..base import BaseServer


class HTTPTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = set_logger(
            self.__class__.__name__,
            verbose=True if '--verbose' in sys.argv else False)

    def send(self, method: str,
             host: str = '127.0.0.1',
             port: int = 80,
             path: str = '/',
             params: dict = None,
             headers: dict = None):

        url = 'http://%s:%s%s' % (host, port, path)
        self.logger.info('SEND: <Request %s %s >' % (method, url))
        response = requests.request(method, url, params=params, headers=headers)
        self.logger.info('RECV: %s' % response)
        self.logger.debug(format_response(response))
        return response

    @staticmethod
    def setUpServer(cls: BaseServer.__class__, cmdline: List):
        parser = set_parser()
        if '--verbose' in sys.argv:
            cmdline += ['--verbose']
        args = parser.parse_args(cmdline)
        server = cls(**vars(args))
        server.start()
        server.is_ready.wait()
        return server
