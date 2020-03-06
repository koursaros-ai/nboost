from nboost.plugins.models.rerank.base import RerankModelPlugin
from nboost import defaults

from typing import List, Tuple

import numpy as np
from tensorflow import keras

class USEClassifierRerankModelPlugin(RerankModelPlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = keras.models.load_model(self.model_dir)

    def rank(self, query: str, choices: List[str],
             filter_results: type(defaults.filter_results) = defaults.filter_results
             ) -> Tuple[List[int], List[float]]:
        scores = self.model.predict([np.array([query]*len(choices)), np.array(choices)])
        scores = scores.flatten()

        sorted_indices = list(np.argsort(scores)[::-1])
        return sorted_indices, scores[sorted_indices]