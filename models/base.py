from ..base import Base
from typing import List, Union
from aiohttp import web


class BaseModel(Base):
    def __init__(self, lr: float = 10e-3, data_dir: str = '/.cache', **kwargs):
        super().__init__(**kwargs)
        self.lr = lr
        self.data_dir = data_dir

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
