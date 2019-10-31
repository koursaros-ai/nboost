
from typing import Tuple, List, Any
from aiohttp import web


class BaseClient:
    def __init__(self, args):
        self.args = args

    def query(self, request: 'web.BaseRequest') -> Tuple[Any, str, List[str], int]:
        """
        :return Tuple(response, query, candidates, topk)
        """
        raise NotImplementedError

    def reorder(self, response: Any, ranks: List[int]) -> dict:
        """
        :return: json response to return to user
        """
        raise NotImplementedError

    def get_candidates(self, response: 'web.Response'):
        """
        :param response: response from index
        :return: ids, candidates
        """
        raise NotImplementedError
