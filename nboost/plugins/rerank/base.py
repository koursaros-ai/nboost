"""Base Class for ranking models"""

from typing import List, Tuple
import time
from nboost.plugins import Plugin
from nboost.delegates import RequestDelegate, ResponseDelegate
from nboost.helpers import calculate_mrr
from nboost.database import DatabaseRow
from nboost import defaults

import numpy as np


class RerankModelPlugin(Plugin):
    """Base class for reranker models"""

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
             filter_results=defaults.filter_results
             ) -> Tuple[List[int], List[float]]:
        """assign relative ranks to each choice"""
        if len(choices) == 0:
            return [], []

        logits = self.get_logits(query, choices)
        scores = []
        all_scores = []
        index_map = []
        for i, logit in enumerate(logits):
            neg_logit = logit[0]
            score = logit[1]
            all_scores.append(score)
            if score > neg_logit or not filter_results:
                scores.append(score)
                index_map.append(i)
        sorted_indices = [index_map[i] for i in np.argsort(scores)[::-1]]
        return sorted_indices, [all_scores[i] for i in sorted_indices]

    def get_logits(self, query: str, choices: List[str]):
        """get search ranking logits for query, choices"""
        raise NotImplementedError()

    def close(self):
        """Close the model"""
