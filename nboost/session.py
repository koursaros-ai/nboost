
from typing import Callable
from nboost import defaults
from nboost.helpers import get_jsonpath, set_jsonpath, flatten
from nboost.exceptions import *


class Session:
    """An exchange between the client and server."""
    def __init__(self, uhost: type(defaults.uhost) = defaults.uhost,
                 uport: type(defaults.uport) = defaults.uport,
                 ussl: type(defaults.ussl) = defaults.ussl,
                 delim: type(defaults.delim) = defaults.delim,
                 topn: type(defaults.topn) = defaults.topn,
                 debug: type(defaults.debug) = defaults.debug,
                 filter_results: type(defaults.filter_results) = defaults.filter_results,
                 qa_threshold: type(defaults.qa_threshold) = defaults.qa_threshold,
                 query_path: type(defaults.query_path) = defaults.query_path,
                 query_prep: type(defaults.query_prep) = defaults.query_prep,
                 topk_path: type(defaults.topk_path) = defaults.topk_path,
                 default_topk: type(defaults.default_topk) = defaults.default_topk,
                 choices_path: type(defaults.choices_path) = defaults.choices_path,
                 cvalues_path: type(defaults.cvalues_path) = defaults.cvalues_path,
                 cids_path: type(defaults.cids_path) = defaults.cids_path, **_):
        self.buffer = bytearray()
        self.request = {
            'version': 'HTTP/1.1',
            'method': 'GET',
            'headers': {},
            'body': {},
            'url': {
                'scheme': '',
                'netloc': '',
                'path': '',
                'params': '',
                'query': {},
                'fragment': ''
            }
        }

        self.response = {
            'version': 'HTTP/1.1',
            'status': 200,
            'reason': 'OK',
            'headers': {},
            'body': {'nboost': {}}
        }

        self.cli_configs = {
            'uhost': uhost,
            'uport': uport,
            'ussl': ussl,
            'delim': delim,
            'topn': topn,
            'debug': debug,
            'query_path': query_path,
            'topk_path': topk_path,
            'default_topk': default_topk,
            'cvalues_path': cvalues_path,
            'cids_path': cids_path,
            'choices_path': choices_path,
            'qa_threshold': qa_threshold,
            'query_prep': query_prep,
            'filter_results': filter_results,
            'rerank_cids': [],
            'qa_cids': {}
        }
        self.stats = {}

    def get_request_path(self, path: str):
        return get_jsonpath(self.request, path)

    def get_response_path(self, path: str):
        return get_jsonpath(self.response, path)

    def set_request_path(self, path: str, value):
        return set_jsonpath(self.request, path, value)

    def set_response_path(self, path: str, value):
        return set_jsonpath(self.response, path, value)

    def add_nboost_response(self, key: str, value) -> None:
        self.response['body']['nboost'][key] = value

    def get_config(self, key: str):
        """Configs are set on either the command line, the json request body
        under the "nboost" key, or in the query parameters."""
        query_configs = self.request['url']['query']
        body_configs = self.request['body'].get('nboost', {})
        request_configs = {**query_configs, **body_configs}
        cli_config = self.cli_configs[key]
        config = request_configs.get(key, cli_config)
        return type(cli_config)(config)

    @property
    def uhost(self) -> type(defaults.uhost):
        return self.get_config('uhost')

    @property
    def uport(self) -> type(defaults.uhost):
        return self.get_config('uport')

    @property
    def ussl(self) -> type(defaults.ussl):
        return self.get_config('ussl')

    @property
    def delim(self) -> type(defaults.delim):
        return self.get_config('delim')

    @property
    def debug(self) -> type(defaults.debug):
        return self.get_config('debug')

    @property
    def query_prep(self) -> type(defaults.query_prep):
        return self.get_config('query_prep')

    @property
    def topn(self) -> type(defaults.topn):
        return self.get_config('topn')

    @property
    def filter_results(self) -> type(defaults.filter_results):
        return self.get_config('filter_results')

    @property
    def qa_threshold(self) -> type(defaults.qa_threshold):
        return self.get_config('qa_threshold')

    @property
    def topk_path(self) -> type(defaults.topk_path):
        return self.get_config('topk_path')

    @property
    def default_topk(self) -> type(defaults.default_topk):
        return self.get_config('default_topk')

    @property
    def query_path(self) -> type(defaults.query_path):
        return self.get_config('query_path')

    @property
    def choices_path(self) -> type(defaults.choices_path):
        return self.get_config('choices_path')

    @property
    def cids_path(self) -> type(defaults.cids_path):
        return self.choices_path + '.[*].' + self.get_config('cids_path')

    @property
    def cvalues_path(self) -> str:
        return self.choices_path + '.[*].' + self.get_config('cvalues_path')

    @property
    def topk(self) -> int:
        topks = self.get_request_path(self.topk_path)
        return int(topks[0]) if topks else self.default_topk

    @property
    def query(self) -> str:
        queries = self.get_request_path(self.query_path)
        query = self.delim.join(queries)

        # check for errors
        if not query:
            raise MissingQuery

        return eval(self.query_prep)(query)

    @property
    def choices(self) -> list:
        choices = self.get_response_path(self.choices_path)

        if not isinstance(choices, list):
            raise InvalidChoices('choices were not a list')

        return flatten(choices)

    @property
    def cids(self) -> list:
        return self.get_response_path(self.cids_path)

    @property
    def cvalues(self) -> list:
        return self.get_response_path(self.cvalues_path)

    @property
    def rerank_cids(self) -> list:
        return self.get_config('rerank_cids')

    @property
    def qa_cids(self) -> dict:
        qa_cids = self.get_config('qa_cids')
        return qa_cids[0] if qa_cids else {}

