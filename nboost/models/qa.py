from typing import Tuple
from nboost.models.base import BaseModel


class QAModel:
    def get_answer(self, question: str, context: str) -> Tuple[str, Tuple[int, int, int]]:
        """Return (answer, (candidate, start_pos, end_pos))"""
