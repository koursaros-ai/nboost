from ..base import *


class TestModel(BaseModel):
    def rank(self, query, choices):
        return list(range(len(choices)))

