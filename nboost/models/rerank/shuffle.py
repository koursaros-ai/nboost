"""Shuffle model"""

from nboost.models.rerank.base import RerankModel
import random


class ShuffleModel(RerankModel):
    """Model that randomly shuffles choices. Useful for benchmarking/testing"""
    def rank(self, query, choices, **kwargs):
        """random shuffle with no regard for query"""
        ranks = list(range(len(choices)))
        random.shuffle(ranks)
        return ranks
