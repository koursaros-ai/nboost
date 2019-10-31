
from typing import Tuple, List, Any
from aiohttp import web


class BaseClient:
    def __init__(self, args):
        self.args = args

    async def query(self, request: 'web.BaseRequest') -> Tuple[Any, str, List[str], int]:
        """
        :return Tuple(response, query, candidates, topk)
        """
        raise NotImplementedError

    def reorder(self, response: Any, ranks: List[int]) -> dict:
        """
        :return: json response to return to user
        """
        raise NotImplementedError

    def get_candidates(self, response: 'web.Response', field: str):
        """
        :param response: response from index
        :param field: field to extract candidates from
        :return: ids, candidates
        """
        raise NotImplementedError
