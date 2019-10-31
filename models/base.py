from typing import List


class BaseModel:
    def __init__(self, args):
        self.args = args

    def rank(self, query: str, candidates: List[str]):
        raise NotImplementedError

    def train(self, query: str, candidates: List[str], labels: List[int]):
        raise NotImplementedError

