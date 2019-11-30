from typing import List, Any, Tuple
from nboost.types import Request, Response


class BaseCodex:
    """The codex class is the search engine api translation protocol. The
    protocol receives incoming http messages and parses them, executing the
    callbacks below.

    The goal of the codex is to efficiently parse the request message and
    magnify it to increase the search results. Then, the protocol should parse
    the query and choices from the amplified search api results for the model
    to rank."""
    SEARCH_PATH = '/search'

    def __init__(self, multiplier: int = 10, **_):
        self.multiplier = multiplier

    def parse_query(self, request: Request) -> Tuple[Any, bytes]:
        """Parse the client request. Autodetect the field.
        :return: Tuple[field, query]"""

    def multiply_request(self, request: Request) -> int:
        """Increase the size of the request and return topk"""

    def parse_choices(self, response: Response, field: str) -> List[bytes]:
        """Parse the all choices from the given field in the response"""

    def reorder_response(self, request: Request, response: Response,
                         ranks: List[int]) -> Response:
        """Reorder the response according the ranks from the model"""
