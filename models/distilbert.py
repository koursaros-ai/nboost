from .base import BaseModel
import torch, torch.nn
import numpy as np

class DBRank(BaseModel):

    def __init__(self, *args, **kwargs):
        from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer, AdamW, ConstantLRSchedule

        super().__init__(*args, **kwargs)
        self.model_name = 'distilbert-base-uncased'
        self.data_dir = '.model-cache/'
        self.lr = 10e-3
        self.max_grad_norm = 1.0
        model_config = AutoConfig.from_pretrained(self.model_name, cache_dir=self.data_dir)
        model_config.num_labels = 1 # set up for regression
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu": print("RUNING ON CPU")
        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(self.model_name,
                                                                               config=model_config,
                                                                               cache_dir=self.data_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.data_dir)
        self.rerank_model.to(self.device)

        self.optimizer = AdamW(self.rerank_model.parameters(), lr=self.lr, correct_bias=False)
        self.scheduler = ConstantLRSchedule(self.optimizer)

    def train(self, query, candidates, labels):
        self(query,candidates,labels=labels)

    def rank(self, query, candidates):
        return self(query,candidates)

    def __call__(self, query, candidates, labels=None):
        """
        :param query: the search query
        :param candidates: the candidate results
        :param labels: optionally train given user feedback
        :return sorted list of indices of topk candidates
        """
        assert(labels is not None or k is not None)


        if labels:
            inputs = []
            for candidate in candidates:
                inputs.append(
                    self.tokenizer.encode_plus(query, candidate, add_special_tokens=True))
            labels = torch.tensor(labels, dtype=torch.float).to(self.device)
        else:
            inputs = [
                self.tokenizer.encode_plus(
                    query,
                    candidate,
                    add_special_tokens=True,
                ) for candidate in candidates]

        max_len = max(len(t['input_ids']) for t in inputs)
        input_ids = [t['input_ids'] + [0] * (max_len - len(t['input_ids'])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids']) + [0] * (max_len - len(t['input_ids'])) for t in inputs]

        input_ids = torch.tensor(input_ids).to(self.device)
        attention_mask = torch.tensor(attention_mask).to(self.device)

        if labels is not None:
            loss = self.rerank_model(input_ids, labels=labels, attention_mask=attention_mask)[0]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.rerank_model.parameters(), self.max_grad_norm)
            self.optimizer.step()
            self.scheduler.step()
            self.rerank_model.zero_grad()
        else:
            with torch.no_grad():
                logits = self.rerank_model(input_ids, attention_mask=attention_mask)[0]
                scores = np.squeeze(logits.detach().cpu().numpy())
                if len(logits) == 1:
                    scores = [scores]
                return list(np.argsort(scores)[::-1])