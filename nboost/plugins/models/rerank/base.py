"""Base Class for ranking models"""

from typing import List, Tuple
import time
from nboost.plugins.models.base import ModelPlugin
from nboost.delegates import RequestDelegate, ResponseDelegate
from nboost.helpers import calculate_mrr
from nboost.database import DatabaseRow
from nboost import defaults


class RerankModelPlugin(ModelPlugin):
    def on_request(self, request: RequestDelegate, db_row: DatabaseRow):
        db_row.topk = request.topk if request.topk else request.default_topk
        request.topk = request.topn

    def on_response(self, response: ResponseDelegate, db_row: DatabaseRow):

        if response.request.rerank_cids:
            db_row.server_mrr = calculate_mrr(
                correct=response.request.rerank_cids.list,
                guesses=response.cids
            )

        start_time = time.perf_counter()

        ranks, scores = self.rank(
            query=response.request.query,
            choices=response.cvalues,
            filter_results=response.request.filter_results
        )
        db_row.rerank_time = time.perf_counter() - start_time

        # raise helpful error if choices is shorter than ranks
        reranked_choices = [response.choices[rank] for rank in ranks]

        response.choices = reranked_choices
        response.set_path('body.nboost.scores', list([float(score) for score in scores]))

        if response.request.rerank_cids:
            db_row.model_mrr = calculate_mrr(
                correct=response.request.rerank_cids.list,
                guesses=response.cids
            )

        response.choices = response.choices[:db_row.topk]

    def rank(self, query: str, choices: List[str],
             filter_results: type(defaults.filter_results) = defaults.filter_results
             ) -> Tuple[List[int], List[float]]:
        """assign relative ranks to each choice"""

    def close(self):
        """Close the model"""
