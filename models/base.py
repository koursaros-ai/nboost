from typing import List


class BaseModel:
    def __init__(self, **kwargs):
        pass

    async def rank(self, query: str, candidates: List[str]) -> List[int]:
        raise NotImplementedError

    async def train(self, query: str, candidates: List[str], labels: List[int]) -> None:
        raise NotImplementedError
