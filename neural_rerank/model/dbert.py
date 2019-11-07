from .base import BaseModel
import torch, torch.nn
import numpy as np
from ..base.types import *


class DBERTModel(BaseModel):
    model_name = 'distilbert-base-uncased'
    max_grad_norm = 1.0

    def __init__(self, *args, **kwargs):
        from transformers import (AutoConfig,
                                  AutoModelForSequenceClassification,
                                  AutoTokenizer,
                                  AdamW,
                                  ConstantLRSchedule)

        super().__init__(*args, **kwargs)
        model_config = AutoConfig.from_pretrained(self.model_name)
        model_config.num_labels = 1  # set up for regression
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu":
            self.logger.info("RUNNING ON CPU")
        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            config=model_config)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.rerank_model.to(self.device, non_blocking=True)

        self.optimizer = AdamW(self.rerank_model.parameters(), lr=self._lr, correct_bias=False)
        self.scheduler = ConstantLRSchedule(self.optimizer)

    async def train(self, query, choices, labels):
        input_ids, attention_mask = await self.encode(query, choices)

        labels = torch.tensor(labels, dtype=torch.float).to(self.device, non_blocking=True)
        loss = self.rerank_model(input_ids, labels=labels, attention_mask=attention_mask)[0]
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.rerank_model.parameters(), self.max_grad_norm)
        self.optimizer.step()
        self.scheduler.step()
        self.rerank_model.zero_grad()

    async def rank(self, query, choices):
        input_ids, attention_mask = await self.encode(query, choices)

        with torch.no_grad():
            logits = self.rerank_model(input_ids, attention_mask=attention_mask)[0]
            scores = np.squeeze(logits.detach().cpu().numpy())
            if len(logits) == 1:
                scores = [scores]
            return Ranks(np.argsort(scores)[::-1])

    async def encode(self, query, choices):
        inputs = [self.tokenizer.encode_plus(
            query, candidate, add_special_tokens=True
        ) for candidate in choices]

        max_len = max(len(t['input_ids']) for t in inputs)
        input_ids = [t['input_ids'] + [0] * (max_len - len(t['input_ids'])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids']) + [0] * (max_len - len(t['input_ids'])) for t in inputs]

        input_ids = torch.tensor(input_ids).to(self.device, non_blocking=True)
        attention_mask = torch.tensor(attention_mask).to(self.device, non_blocking=True)

        return input_ids, attention_mask
