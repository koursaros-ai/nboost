
import requests
from .utils import *


class ESClient:
    def __init__(self, args):
        self.args = args

    def query(self, data):
        pass


class TestClient:
    def query(self, data):
        return FAKE_ES_DATA


class MutliSearchClient:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = f'http://%s:%s/%s/_msearch' % (
            self.args.es_host, self.args.es_port, self.args.es_index)

    def query(self, data):
        requests.post(self.uri, data=data, headers={'Content-Type': 'application/json'})