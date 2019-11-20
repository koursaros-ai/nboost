from ..base import *
import random


class TestModel(BaseModel):
    def rank(self, query, choices):
        ranks = list(range(len(choices)))
        random.shuffle(ranks)
        return ranks

