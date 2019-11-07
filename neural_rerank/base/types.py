from typing import NamedTuple, List
from enum import Enum


class Route(Enum):
    SEARCH = 0
    TRAIN = 1
    STATUS = 2
    NOT_FOUND = 3
    ERROR = 4


class Request(NamedTuple):
    method: str
    path: str
    headers: dict
    params: dict
    body: bytes


class Response(NamedTuple):
    headers: dict
    body: bytes
    status: int


class Choice(NamedTuple):
    id: int
    body: bytes


class Labels(List[float]):
    pass


class Cid(int):
    pass


class Query(str):
    pass


class Ranks(List[int]):
    pass
