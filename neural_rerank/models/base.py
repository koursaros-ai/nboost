from ..base import Base
from .handler import ModelHandler
from typing import List, Union
from aiohttp import web


class BaseModel(Base):
    handler = ModelHandler()

    def __init__(self,
                 lr: float = 10e-3,
                 data_dir: str = '/.cache',
                 **kwargs):
        super().__init__(**kwargs)
        self._lr = lr
        self._data_dir = data_dir

    @handler.add_state
    def lr(self):
        return self._lr

    @handler.add_state
    def data_dir(self):
        return self._data_dir

    async def train(self,
                    query: str,
                    candidates: List[str],
                    labels: List[Union[int, float]]) -> None:
        """
        :param query: the search query
        :param candidates: the candidate results
        :param labels: optionally train given user feedback
        """
        raise web.HTTPNotImplemented

    async def rank(self, query: str, candidates: List[str]) -> List[int]:
        """
        :param query: the search query
        :param candidates: the candidate results
        :return sorted list of indices of topk candidates
        """
        raise web.HTTPNotImplemented
