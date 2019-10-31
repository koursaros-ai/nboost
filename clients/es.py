from .base import BaseClient
from typing import Tuple, List, Any

from aiohttp import web

class ESClient (BaseClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def query(self, request: 'web.BaseRequest') -> Tuple[Any, str, List[str], int]:
        return

    def reorder(self, response: Any, ranks: List[int]) -> dict:
        return