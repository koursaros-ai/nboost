from .base import BaseModel


class TestModel(BaseModel):

    def train(self, query, candidates, labels):
        pass

    def rank(self, query, candidates, topk):
        return list(range(0, topk))
