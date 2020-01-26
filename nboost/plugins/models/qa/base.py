from typing import Tuple
import time
from nboost.plugins.models.base import ModelPlugin
from nboost.delegates import ResponseDelegate
from nboost.database import DatabaseRow
from nboost import defaults


class QAModelPlugin(ModelPlugin):
    def __init__(self, max_query_length: type(defaults.max_query_length) = defaults.max_query_length,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_query_length = max_query_length

    def on_response(self, response: ResponseDelegate, db_row: DatabaseRow):
        if response.cvalues:
            start_time = time.perf_counter()

            answer, start_pos, stop_pos, score = self.get_answer(
                response.request.query,
                response.cvalues[0])

            db_row.qa_time = time.perf_counter() - start_time

            if score > response.request.qa_threshold:
                response.set_path('json.nboost.answer_text', answer)
                response.set_path('json.nboost.answer_start_pos', start_pos)
                response.set_path('json.nboost.answer_stop_pos', stop_pos)

    def get_answer(self, query: str, cvalue: str) -> Tuple[str, int, int, float]:
        """Return answer, start_pos, end_pos, score"""
