from ..base import StatefulBase
from aiohttp import web
from ..base.types import *
import os


class BaseModel(StatefulBase):
    def __init__(self,
                 lr: float = 10e-3,
                 model_ckpt: str ='./marco_bert',
                 data_dir: str = './.cache',
                 max_seq_len: int = 128,
                 batch_size: int = 4, **kwargs):
        super().__init__()
        self.lr = lr
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_dir = data_dir
        self.model_ckpt = model_ckpt
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size

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
