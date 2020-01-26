
from typing import Optional
from nboost.helpers import get_jsonpath, set_jsonpath, JSONTYPES, flatten
from nboost.exceptions import *
from nboost import defaults


class Delegate:
    """A Class that parses the attributes of a request or response. It is
     configured by command line and runtime arguments. Also used for setting
     the request/response prior to preparation."""
    def __init__(self):
        self.dict = None  # type: Optional[dict]

    def get_path(self, path: str) -> JSONTYPES:
        return get_jsonpath(self.dict, path)

    def set_path(self, path: str, value: JSONTYPES):
        set_jsonpath(self.dict, path, value)


class RequestDelegate(Delegate):
    def __init__(self, dict_request: dict,
                 uhost: type(defaults.uhost) = defaults.uhost,
                 uport: type(defaults.uport) = defaults.uport,
                 ussl: type(defaults.ussl) = defaults.ussl,
                 query_delim: type(defaults.query_delim) = defaults.query_delim,
                 topn: type(defaults.topn) = defaults.topn,
                 query_prep: type(defaults.query_prep) = defaults.query_prep,
                 topk_path: type(defaults.topk_path) = defaults.topk_path,
                 default_topk: type(defaults.default_topk) = defaults.default_topk,
                 query_path: type(defaults.query_path) = defaults.query_path,
                 rerank_cids: type(defaults.rerank_cids) = defaults.rerank_cids,
                 choices_path: type(defaults.choices_path) = defaults.choices_path,
                 cvalues_path: type(defaults.cvalues_path) = defaults.cvalues_path,
                 cids_path: type(defaults.cids_path) = defaults.cids_path,
                 filter_results: type(defaults.filter_results) = defaults.filter_results,
                 qa_threshold: type(defaults.qa_threshold) = defaults.qa_threshold,
                 **_):
        super().__init__()
        self.dict = dict_request
        self.uhost = type(defaults.uhost)(uhost)
        self.uport = type(defaults.uport)(uport)
        self.ussl = type(defaults.ussl)(ussl)
        self.query_path = type(defaults.query_path)(query_path)
        self.query_delim = type(defaults.query_delim)(query_delim)
        self.query_prep = type(defaults.query_prep)(query_prep)
        self.topn = type(defaults.topn)(topn)
        self.topk_path = type(defaults.topk_path)(topk_path)
        self.default_topk = type(defaults.default_topk)(default_topk)
        self.rerank_cids = type(defaults.rerank_cids)(rerank_cids)
        self.choices_path = type(defaults.choices_path)(choices_path)
        self.cvalues_path = type(defaults.cvalues_path)(cvalues_path)
        self.cids_path = type(defaults.cids_path)(cids_path)
        self.filter_results = type(defaults.filter_results)(filter_results)
        self.qa_threshold = type(defaults.qa_threshold)(qa_threshold)

    @property
    def topk(self) -> int:
        topks = self.get_path(self.topk_path)
        return int(topks[0]) if topks else self.default_topk

    @topk.setter
    def topk(self, value: int):
        self.set_path(self.topk_path, value)

    @property
    def query(self) -> str:
        queries = self.get_path(self.query_path)
        query = self.query_delim.join(queries)

        # check for errors
        if not query:
            raise MissingQuery

        return eval(self.query_prep)(query)


class ResponseDelegate(Delegate):
    def __init__(self, dict_response: dict, request: RequestDelegate, **_):
        super().__init__()
        self.dict = dict_response
        self.request = request

    @property
    def choices(self) -> list:
        choices = self.get_path(self.request.choices_path)

        if not isinstance(choices, list):
            raise InvalidChoices('choices were not a list')

        return flatten(choices)

    @choices.setter
    def choices(self, value: list):
        self.set_path(self.request.choices_path, value)

    @property
    def cids(self) -> list:
        return self.get_path(
            self.request.choices_path + '.[*].' + self.request.cids_path
        )

    @property
    def cvalues(self) -> list:
        return self.get_path(
            self.request.choices_path + '.[*].' + self.request.cvalues_path
        )
