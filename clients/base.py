
from typing import Tuple, List, Any


class BaseClient:
    def __init__(self, args):
        self.args = args

    def query(self, query: str, size: int) -> Tuple[List[str], Any]:
        """
        :param query: the user's query
        :param size: the user's desired number of results
        :return Tuple(fields, full data)
        """
        raise NotImplementedError

    def reorder(self, full: Any, ranks: List[int]) -> dict:
        """
        :param full: the full result of the query
        :param ranks: the ranks of the fields
        :return: json response to return to user
        """
        raise NotImplementedError
