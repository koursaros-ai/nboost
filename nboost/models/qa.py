from typing import Tuple
from nboost.models.base import BaseModel


class QAModel(BaseModel):
    def __init__(self, *args, max_query_length=64, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_query_length = max_query_length

    def get_answer(self, query: str, choice: str) -> Tuple[str, Tuple[int, int, int], float]:
        """Return (answer, (start_pos, end_pos, cid), score)"""
