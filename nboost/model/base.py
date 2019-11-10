from ..base import StatefulBase
from aiohttp import web
from ..base.types import *


class BaseModel(StatefulBase):
    def __init__(self,
                 lr: float = 10e-3,
                 model_ckpt: str ='./marco_bert',
                 data_dir: str = '/.cache', **kwargs):
        super().__init__()
        self.lr = lr
        self.data_dir = data_dir
        self.model_ckpt = model_ckpt

    def post_start(self):
        """ Executes after the process forks """
        pass

    def state(self):
        return dict(lr=self.lr, data_dir=self.data_dir)

    def train(self, query: Query, choices: Choices, labels: Labels) -> None:
        """ train """
        raise web.HTTPNotImplemented

    def rank(self, query: Query, choices: Choices) -> Ranks:
        """
        sort list of indices of topk candidates
        """
        raise web.HTTPNotImplemented
