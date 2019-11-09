from ..base.types import Ranks
from .base import BaseModel
import torch, torch.nn
import numpy as np
import os


class DBERTModel(BaseModel):
    model_name = 'distilbert-base-uncased'
    max_grad_norm = 1.0
    max_seq_len = 128

    def __init__(self, *args, **kwargs):
        from transformers import (AutoConfig,
                                  AutoModelForSequenceClassification,
                                  AutoTokenizer,
                                  AdamW,
                                  ConstantLRSchedule)

        super().__init__(*args, **kwargs)
        self.model_path = '.distilbert/'
        self.train_steps = 0
        self.checkpoint_steps = 500

        if os.path.exists(os.path.join(self.model_path, 'config.json')):
            self.model_name = self.model_path

        model_config = AutoConfig.from_pretrained(self.model_name)
        model_config.num_labels = 1  # set up for regression
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.device == torch.device("cpu"):
            self.logger.info("RUNNING ON CPU")
        else:
            self.logger.info("RUNNING ON CUDA")
            torch.cuda.synchronize(self.device)

        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            config=model_config)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.rerank_model.to(self.device, non_blocking=True)

        self.optimizer = AdamW(self.rerank_model.parameters(), lr=self.lr, correct_bias=False)
        self.scheduler = ConstantLRSchedule(self.optimizer)

        self.weight = 0.0

    async def train(self, query, choices, labels):
        input_ids, attention_mask = await self.encode(query, choices)

        labels = torch.tensor(labels, dtype=torch.float).to(self.device, non_blocking=True)
        loss = self.rerank_model(input_ids, labels=labels, attention_mask=attention_mask)[0]
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.rerank_model.parameters(), self.max_grad_norm)
        self.optimizer.step()
        self.scheduler.step()
        self.rerank_model.zero_grad()
        self.train_steps += 1
        if self.weight < 1.0:
            self.weight += self.lr*0.1
        if self.train_steps % self.checkpoint_steps == 0:
            await self.save()

    async def rank(self, query, choices):
        input_ids, attention_mask = await self.encode(query, choices)

        with torch.no_grad():
            logits = self.rerank_model(input_ids, attention_mask=attention_mask)[0]
            scores = np.squeeze(logits.detach().cpu().numpy())
            if len(logits) == 1:
                scores = [scores]
            es_ranks = np.arange(len(scores))
            model_ranks = np.argsort(scores)[::-1]
            avg_rank = self.weight*model_ranks + (1-self.weight)*es_ranks
            self.logger.info(self.weight)
            return Ranks(np.argsort(avg_rank))

    async def encode(self, query, choices):
        inputs = [self.tokenizer.encode_plus(
            query, choice.decode(), add_special_tokens=True
        ) for choice in choices]

        max_len = min(max(len(t['input_ids']) for t in inputs), self.max_seq_len)
        input_ids = [t['input_ids'][:max_len] + [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids'][:max_len]) +
                          [0] * (max_len - len(t['input_ids'][:max_len])) for t in inputs]

        input_ids = torch.tensor(input_ids).to(self.device, non_blocking=True)
        attention_mask = torch.tensor(attention_mask).to(self.device, non_blocking=True)

        return input_ids, attention_mask

    async def save(self):
        self.logger.info('Saving model')
        os.makedirs(self.model_path, exist_ok=True)
        self.rerank_model.save_pretrained(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
