from typing import Tuple
from nboost.models.base import BaseModel


class QAModel(BaseModel):
    QA_MODEL_DIR = str()

    def __init__(self, qa_model_dir=str(), max_query_length=64, **kwargs):
        super().__init__(**kwargs)
        qa_model_dir = qa_model_dir if qa_model_dir else self.QA_MODEL_DIR
        self.model_dir = self.resolve_model_dir(qa_model_dir)
        self.max_query_length = max_query_length

    def get_answer(self, question: str, context: str) -> Tuple[str, Tuple[int, int, int]]:
        """Return (answer, (candidate, start_pos, end_pos))"""
