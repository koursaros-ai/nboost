from ..base import BaseModel
import os

from transformers import (AutoConfig,
                          AutoModelForSequenceClassification,
                          AutoTokenizer,
                          AdamW,
                          ConstantLRSchedule)
import torch, torch.nn
import numpy as np


class TransformersModel(BaseModel):
    max_grad_norm = 1.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download()
        self.train_steps = 0
        self.checkpoint_steps = 500
        self.model_ckpt = str(self.model_dir.name)
        self.distilbert = 'distilbert' in self.model_ckpt

        if os.path.exists(os.path.join(self.model_ckpt, 'config.json')):
            self.logger.info('Loading from checkpoint %s' % self.model_ckpt)
            self.model_config = AutoConfig.from_pretrained(self.model_ckpt)
        elif os.path.exists(os.path.join(self.data_dir, 'config.json')):
            self.logger.info('Loading from trained model in %s' % self.data_dir)
            self.model_ckpt = self.data_dir
            self.model_config = AutoConfig.from_pretrained(self.model_ckpt)
        else:
            self.logger.info(
                'Initializing new model with pretrained weights %s' % self.model_ckpt)
            self.model_config = AutoConfig.from_pretrained(self.model_ckpt)
            self.model_config.num_labels = 1  # set up for regression

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if self.device == torch.device("cpu"):
            self.logger.info("RUNNING ON CPU")
        else:
            self.logger.info("RUNNING ON CUDA")
            torch.cuda.synchronize(self.device)

        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(
            self.model_ckpt,
            config=self.model_config)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_ckpt)
        self.rerank_model.to(self.device, non_blocking=True)

        self.optimizer = AdamW(self.rerank_model.parameters(), lr=self.lr, correct_bias=False)
        self.scheduler = ConstantLRSchedule(self.optimizer)

        self.weight = 1.0

    def train(self, query, choices):
        input_ids, attention_mask, token_type_ids = self.encode(query, choices)

        if self.model_config.num_labels == 1:
            labels = torch.tensor(labels, dtype=torch.float).to(self.device, non_blocking=True)
        else:
            labels = torch.tensor(labels, dtype=torch.long).to(self.device, non_blocking=True)

        if self.distilbert:
            loss = self.rerank_model(input_ids,labels=labels,attention_mask=attention_mask)[0]
        else:
            loss = self.rerank_model(input_ids,
                                     labels=labels,
                                     attention_mask=attention_mask,
                                     token_type_ids=token_type_ids)[0]
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.rerank_model.parameters(), self.max_grad_norm)
        self.optimizer.step()
        self.scheduler.step()
        self.rerank_model.zero_grad()
        self.train_steps += 1
        if self.weight < 1.0:
            self.weight += self.lr*0.1
        if self.train_steps % self.checkpoint_steps == 0:
            self.save()

    def rank(self, query, choices):
        input_ids, attention_mask, token_type_ids = self.encode(query, choices)

        with torch.no_grad():
            if self.distilbert:
                logits = self.rerank_model(input_ids, attention_mask=attention_mask)[0]
            else:
                logits = self.rerank_model(input_ids,
                                           attention_mask=attention_mask,
                                           token_type_ids=token_type_ids)[0]
            scores = np.squeeze(logits.detach().cpu().numpy())
            if len(scores.shape) > 1 and scores.shape[1] == 2:
                scores = np.squeeze(scores[:,1])
            if len(logits) == 1:
                scores = [scores]
            return np.argsort(scores)[::-1]

    def encode(self, query, choices):
        inputs = [self.tokenizer.encode_plus(
            query, choice, add_special_tokens=True) for choice in choices]

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

    def save(self):
        self.logger.info('Saving model')
        os.makedirs(self.data_dir, exist_ok=True)
        self.rerank_model.save_pretrained(self.data_dir)
        self.tokenizer.save_pretrained(self.data_dir)
