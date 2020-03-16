from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List
import numpy as np
import torch.nn
import torch
from nboost.plugins.models.rerank.base import RerankModelPlugin
from nboost import defaults

MAX_BATCH_SIZE=32


class PtBertRerankModelPlugin(RerankModelPlugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info('Loading from checkpoint %s' % self.model_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.device == torch.device("cpu"):
            self.logger.info("RUNNING ON CPU")
        else:
            self.logger.info("RUNNING ON CUDA")
            torch.cuda.synchronize(self.device)

        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        except:
            self.logger.warn('Unable to find tokenizer, using bert or albert tokenizer by default')
            if 'albert' in self.model_dir:
                self.tokenizer = AutoTokenizer.from_pretrained('albert-base-v2')
            else:
                self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.rerank_model.to(self.device, non_blocking=True)

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

        with torch.no_grad():
            logits = self.rerank_model(input_ids,
                                       attention_mask=attention_mask,
                                       token_type_ids=token_type_ids)[0]
            logits = logits.detach().cpu().numpy()

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

        input_ids = torch.tensor(input_ids).to(self.device, non_blocking=True)
        attention_mask = torch.tensor(attention_mask).to(self.device, non_blocking=True)
        token_type_ids = torch.tensor(token_type_ids).to(self.device, non_blocking=True)

        return input_ids, attention_mask, token_type_ids
