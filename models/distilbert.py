from transformers import *
import torch, torch.nn
import numpy as np

class DBRank(object):

    def __init__(self, *args, **kwargs):

        self.model_name = 'distilibert'
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

    def __call__(self, query, candidates, labels=None):

        if labels is not None:
            inputs = []
            labels = []
            for candidate, label in zip(candidates, labels):
                inputs.append(
                    self.tokenizer.encode_plus(query, candidate, add_special_tokens=True))
                labels.append(label)

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
        token_type_ids = [t['token_type_ids'] + [4] * (max_len - len(t['token_type_ids'])) for t in inputs]
        attention_mask = [[1] * len(t['input_ids']) + [0] * (max_len - len(t['input_ids'])) for t in inputs]

        input_ids = torch.tensor(input_ids).to(self.device)
        token_type_ids = torch.tensor(token_type_ids).to(self.device)
        attention_mask = torch.tensor(attention_mask).to(self.device)

        if labels is not None:
            loss = self.rerank_model(input_ids, token_type_ids=token_type_ids,
                                     labels=labels, attention_mask=attention_mask)[0]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.rerank_model.parameters(), self.max_grad_norm)
            self.optimizer.step()
            self.scheduler.step()
            self.rerank_model.zero_grad()
        else:
            with torch.no_grad():
                logits = self.rerank_model(input_ids, token_type_ids=token_type_ids,
                                           attention_mask=attention_mask)[0]
                scores = np.squeeze(logits.detach().cpu().numpy())
                if len(logits) == 1:
                    scores = [scores]
            return scores