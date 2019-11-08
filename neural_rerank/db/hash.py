from .base import BaseDb


class HashDb(BaseDb):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries = dict()
        self.choices = dict()
        self.times = dict()

    def save(self, query, choices):
        qid = hash(query)
        cids = [choice.id for choice in choices]
        self.queries[qid] = query, cids

        for choice in choices:
            self.choices[choice.id] = qid, choice

    def get(self, pick):
        qid, _ = self.choices[pick]
        query, cids = self.queries[qid]
        choices = [self.choices[cid][1] for cid in cids]
        labels = [1.0 if cid == pick else 0.0 for cid in cids]
        return query, choices, labels

    def lap(self, ms, cls, func):
        ident = (cls, func)
        avg_time, laps = self.times[ident] if ident in self.times else 0, 0
        avg_time, laps = (avg_time * laps + ms) / (laps + 1), laps + 1
        self.times[ident] = avg_time, laps
        self.logger.info('%s.%s() avg time is %s ms (pass %s)' % (cls, func, avg_time, laps))

    def state(self):
        return {'times': {'%s.%s' % (cls, func): self.times[(cls, func)] for cls, func in self.times}}
