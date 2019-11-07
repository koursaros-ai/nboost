
from .base import BaseDb


class HashDb(BaseDb):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries = dict()
        self.choices = dict()

    def save(self, query, choices):
        qid = hash(query)
        cids = [choice.id for choice in choices]
        self.queries[qid] = query, cids

        for choice in choices:
            self.choices[choice.id] = qid, choice

    def get(self, pick):
        qid, _ = self.choices[pick]
        query, cids = self.queries[qid]
        choices = [self.choices[cid] for cid in cids]
        labels = [1.0 if cid == pick else 0.0 for cid in cids]
        return query, choices, labels
