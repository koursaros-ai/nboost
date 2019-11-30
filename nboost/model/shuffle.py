"""Shuffle model"""

from nboost.model.base import BaseModel
import random


class ShuffleModel(BaseModel):
    """Model that randomly shuffles choices. Useful for benchmarking/testing"""
    def rank(self, query, choices):
        """random shuffle with no regard for query"""
        ranks = list(range(len(choices)))
        random.shuffle(ranks)
        return ranks
