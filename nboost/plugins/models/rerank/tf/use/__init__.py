import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import tensorflow_text
from nboost.plugins.models.rerank.base import RerankModelPlugin
from nboost import defaults

from typing import List, Tuple

class USERerankModelPlugin(RerankModelPlugin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-qa/3')


    def rank(self, query: str, choices: List[str],
             filter_results: type(defaults.filter_results) = defaults.filter_results
             ) -> Tuple[List[int], List[float]]:
        questions = [query]

        question_embeddings = self.module.signatures['question_encoder'](
            tf.constant(questions))
        response_embeddings = self.module.signatures['response_encoder'](
            input=tf.constant(choices),
            context=tf.constant(choices))

        scores = np.inner(question_embeddings['outputs'], response_embeddings['outputs'])
        scores = np.reshape(scores, (-1,))
        sorted_indices = list(np.argsort(scores)[::-1])
        return sorted_indices, scores[sorted_indices]




