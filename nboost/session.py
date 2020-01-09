
from nboost import defaults
from nboost.helpers import get_jsonpath, set_jsonpath, flatten
from nboost.exceptions import *

RERANK_CIDS = '(body.nboost.rerank.cids) | (url.rerank_cids)'
QA_CIDS = 'body.nboost.qa.cids'


class Session:
    """An exchange between the client and server."""
    def __init__(self, delim: type(defaults.delim) = defaults.delim,
                 query_path: type(defaults.query_path) = defaults.query_path,
                 topk_path: type(defaults.topk_path) = defaults.topk_path,
                 default_topk: type(defaults.default_topk) = defaults.default_topk,
                 cvalues_path: type(defaults.cvalues_path) = defaults.cvalues_path,
                 cids_path: type(defaults.cids_path) = defaults.cids_path,
                 choices_path: type(defaults.choices_path) = defaults.choices_path,
                 multiplier: type(defaults.multiplier) = defaults.multiplier):
        self.buffer = bytearray()
        self.request = {}
        self.response = {}
        self.multiplier = multiplier
        self.delim = delim
        self._query_path = query_path
        self._topk_path = topk_path
        self._default_topk = default_topk
        self._cvalues_path = cvalues_path
        self._cids_path = cids_path
        self._choices_path = choices_path

    def set_request_path(self, path: str, value):
        return set_jsonpath(self.request, path, value)

    def set_response_path(self, path: str, value):
        return set_jsonpath(self.response, path, value)

    @property
    def nboost_configs(self) -> dict:
        return self.request.get('body', {}).get('nboost', {})

    @property
    def topk_path(self) -> str:
        return self.nboost_configs.get('topk_path', self._topk_path)

    @property
    def topk(self) -> int:
        topks = get_jsonpath(self.request, self.topk_path)
        return int(topks[0]) if topks else self.default_topk

    @property
    def default_topk(self) -> str:
        return self.nboost_configs.get('default_topk', self._default_topk)

    @property
    def query_path(self) -> str:
        return self.nboost_configs.get('query_path', self._query_path)

    @property
    def query(self) -> str:
        queries = get_jsonpath(self.request, self.query_path)
        query = self.delim.join(queries)

        # check for errors
        if not query:
            raise MissingQuery

        return query

    @property
    def choices_path(self) -> str:
        return self.nboost_configs.get('choices_path', self._choices_path)

    @property
    def choices(self) -> list:
        choices = get_jsonpath(self.response, self.choices_path)

        if not isinstance(choices, list):
            raise InvalidChoices('choices were not a list')

        return flatten(choices)

    @property
    def cids_path(self) -> str:
        return self.choices_path + '.[*].' + self.nboost_configs.get('cids_path', self._cids_path)

    @property
    def cids(self) -> list:
        cids = get_jsonpath(self.response, self.cids_path)
        return flatten(cids)

    @property
    def cvalues_path(self) -> str:
        return self.choices_path + '.[*].' + self.nboost_configs.get('cvalues_path', self._cvalues_path)

    @property
    def cvalues(self) -> list:
        return get_jsonpath(self.response, self.cvalues_path)

    @property
    def rerank_cids(self) -> list:
        rerank_cids = get_jsonpath(self.request, RERANK_CIDS)
        return flatten(rerank_cids)

    @property
    def qa_cids(self) -> dict:
        qa_cids = get_jsonpath(self.request, QA_CIDS)
        return qa_cids[0] if qa_cids else None

