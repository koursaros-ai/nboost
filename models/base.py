from typing import List


class BaseModel:
    def __init__(self, **kwargs):
        pass

    def rank(self, query: str, candidates: List[str]) -> List[int]:
        raise NotImplementedError

    def train(self, query: str, candidates: List[str], labels: List[int]) -> None:
        raise NotImplementedError
