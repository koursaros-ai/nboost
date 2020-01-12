from typing import Tuple
from nboost.models.base import BaseModel
from nboost import defaults


class QAModel(BaseModel):
    def __init__(self, max_query_length: type(defaults.max_query_length) = defaults.max_query_length,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_query_length = max_query_length

    def get_answer(self, query: str, choice: str) -> Tuple[str, int, int, float]:
        """Return answer, start_pos, end_pos, score"""
