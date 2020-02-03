"""Shuffle model"""

from nboost.plugins.models.rerank.base import RerankModelPlugin
import random


class ShuffleRerankModelPlugin(RerankModelPlugin):
    """Model that randomly shuffles choices. Useful for benchmarking/testing"""
    def rank(self, query, choices, **kwargs):
        """random shuffle with no regard for query"""
        ranks = list(range(len(choices)))
        random.shuffle(ranks)
        scores = [0] * len(ranks)
        return ranks, scores
