from ..base import *
import random


class TestModel(BaseModel):
    def rank(self, query, choices):
        # random ranking
        ranks = list(range(0, len(choices)))
        random.shuffle(ranks)
        for i, rank in enumerate(ranks):
            choices[i].rank = rank

    def train(self, query, choices):
        pass
