from ..base.model import BaseModel


class TestModel(BaseModel):

    def train(self, query, candidates, labels):
        pass

    def rank(self, query, candidates):
        return list(range(0, len(candidates)))
