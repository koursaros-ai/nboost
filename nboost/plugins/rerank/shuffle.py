"""Shuffle model"""

from nboost.plugins.rerank.base import RerankModelPlugin
import numpy as np


class ShuffleRerankPlugin(RerankModelPlugin):
    """Model that randomly shuffles choices. Useful for benchmarking/testing"""
    def get_logits(self, query, choices, **kwargs):
        """random shuffle with no regard for query"""
        return np.zeros((len(choices), 2))
