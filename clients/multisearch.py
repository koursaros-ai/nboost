from .base import BaseClient
import requests


class MutliSearchClient(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uri = 'http://%s:%s/%s/_msearch' % (
            self.args.es_host, self.args.es_port, self.args.es_index)

    def query(self, query, size):
        requests.post(self.uri, data=query, headers={'Content-Type': 'application/json'})