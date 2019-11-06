from .base import BaseModel
import random


class TestModel(BaseModel):
    async def rank(self, query, candidates):
        # random ranking
        ranks = list(range(0, len(candidates)))
        random.shuffle(ranks)
        return ranks

    async def train(self, query, candidates, labels):
        pass
