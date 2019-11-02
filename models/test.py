from ..models.base import BaseModel


class TestModel(BaseModel):

    async def train(self, query, candidates, labels):
        pass

    async def rank(self, query, candidates):
        return list(range(0, len(candidates)))
