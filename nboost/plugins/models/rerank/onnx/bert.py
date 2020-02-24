from transformers import AutoTokenizer
from typing import List
import numpy as np
from nboost.plugins.models.rerank.base import RerankModelPlugin
from nboost import defaults
import onnxruntime as rt
import glob
import os


class ONNXBertRerankModelPlugin(RerankModelPlugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sess_options = rt.SessionOptions()

        self.model_dir = glob.glob(os.path.join(self.model_dir, '*.onnx'))[0]

        # Set graph optimization level to ORT_ENABLE_EXTENDED to enable bert optimization.
        sess_options.graph_optimization_level = rt.GraphOptimizationLevel.ORT_ENABLE_EXTENDED

        # To enable model serialization and store the optimized graph to desired location.
        sess_options.optimized_model_filepath = self.model_dir
        self.session = rt.InferenceSession(self.model_dir, sess_options)
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

    def rank(self, query: str, choices: List[str],
             filter_results=defaults.filter_results):
        """
        :param query:
        :param choices:
        :param filter_results:
        :return:
        """
        if len(choices) == 0:
            return [], []
        input_ids, attention_mask, token_type_ids = self.encode(query, choices)

        scores = np.array(self.session.run(None, {
            'input_ids': np.array(input_ids), #.reshape(-1, self.max_seq_len),
            'input_mask': np.array(attention_mask), #.reshape(-1, self.max_seq_len),
            'segment_ids': np.array(token_type_ids) #.reshape(-1, self.max_seq_len)
        }))[0]

        if filter_results:
            scores = np.extract(scores[:, 0] < scores[:, 1], scores)
        if len(scores.shape) > 1 and scores.shape[1] == 2:
            scores = np.reshape(scores[:, 1], (-1,))
        sorted_indices = list(np.argsort(scores)[::-1])
        return sorted_indices, scores

    def encode(self, query: str, choices: List[str]):
        """
        :param query:
        :param choices:
        :return:
        """
        inputs = [self.tokenizer.encode_plus(query, choice, add_special_tokens=True)
                  for choice in choices]

        max_len = min(max(len(t['input_ids']) for t in inputs), self.max_seq_len)
        input_ids = [t['input_ids'][:max_len] +
                     [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids'][:max_len]) +
                          [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]
        token_type_ids = [t['token_type_ids'][:max_len] +
                          [0] * (max_len - len(t['token_type_ids'][:max_len])) for t in inputs]

        # input_ids = torch.tensor(input_ids).to(self.device, non_blocking=True)
        # attention_mask = torch.tensor(attention_mask).to(self.device, non_blocking=True)
        # token_type_ids = torch.tensor(token_type_ids).to(self.device, non_blocking=True)

        return input_ids, attention_mask, token_type_ids