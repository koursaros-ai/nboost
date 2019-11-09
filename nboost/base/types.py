from typing import NamedTuple, List
from enum import Enum


class Route(Enum):
    """Used as keys for the route dictionary created by the proxy."""
    SEARCH = 0
    TRAIN = 1
    STATUS = 2
    NOT_FOUND = 3
    ERROR = 4


class Request(NamedTuple):
    """The object that the server/codex must pack all requests into. This is
    necessary to support multiple search apis."""
    method: str
    path: str
    headers: dict
    params: dict
    body: bytes


class Response(NamedTuple):
    """The object that each response must be packed into before sending. Same
    reason as the Request object. """
    headers: dict
    body: bytes
    status: int


class Choices(List[bytes]):
    """A list of candidates returned by the search api """


class Labels(List[float]):
    """A list of floats representing the labels for a respective list of
    choices."""


class Qid(int):
    """An integer representing a query id. """


class Cid(int):
    """An integer representing a choice id. """


class Query(str):
    """A query from the client """


class Ranks(List[int]):
    """A list of integers representing the relative ranks for a respective
    list of choices. For example, for Ranks(4, 3, 1, 2) the first choice has
    is the worst candidate and the third choice is the best (1st). """
