
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List
import torch.nn
import torch
from nboost.plugins.rerank.base import RerankModelPlugin
from nboost import defaults
from nboost.logger import set_logger


class PtTransformersRerankPlugin(RerankModelPlugin):
    """Reranker models based on huggingface/transformers library"""

    def __init__(self,
                 model_dir: str = 'nboost/pt-tinybert-msmarco',
                 verbose: bool = defaults.verbose,
                 max_seq_len: int = defaults.max_seq_len,
                 **kwargs):
        super().__init__(**kwargs)
        self.logger = set_logger(model_dir, verbose=verbose)
        self.max_seq_len = max_seq_len

        self.logger.info('Loading from checkpoint %s' % model_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.device == torch.device("cpu"):
            self.logger.info("RUNNING ON CPU")
        else:
            self.logger.info("RUNNING ON CUDA")
            torch.cuda.synchronize(self.device)

        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=True)

        self.rerank_model.to(self.device, non_blocking=True)

    def get_logits(self, query: str, choices: List[str]):
        """
        :param query:
        :param choices:
        :return: logits
        """
        input_ids, attention_mask, token_type_ids = self.encode(query, choices)

        with torch.no_grad():
            logits = self.rerank_model(input_ids,
                                       attention_mask=attention_mask,
                                       token_type_ids=token_type_ids)[0]
            logits = logits.detach().cpu().numpy()

            return logits

    def encode(self, query: str, choices: List[str]):
        """
        :param query:
        :param choices:
        :return: Encoded tokens
        """
        inputs = [self.tokenizer.encode_plus(
            query, choice, add_special_tokens=True, return_token_type_ids=True, max_length=self.max_seq_len
            ) for choice in choices]

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
