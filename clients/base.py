
from typing import Tuple, List, Any
from aiohttp import web


class BaseClient:
    def __init__(self, args):
        self.args = args

    def query(self, request: 'web.BaseRequest') -> Tuple[Any, List[str], str]:
        """
        :return Tuple(response, candidates, query)
        """
        raise NotImplementedError

    def reorder(self, response: Any, ranks: List[int]) -> dict:
        """
        :return: json response to return to user
        """
        raise NotImplementedError
