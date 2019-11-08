from .base import BaseDb


class HashDb(BaseDb):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries = dict()
        self.choices = dict()
        self.laps = dict()

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

        if cls not in self.laps:
            self.laps[cls] = {func: dict(avg_ms=ms, laps=1)}
        elif func not in self.laps[cls]:
            self.laps[cls][func] = dict(avg_ms=ms, laps=1)
        else:
            ident = self.laps[cls][func]
            ident['laps'] += 1
            ident['avg_ms'] = (ident['avg_ms'] * (ident['laps'] - 1) + ms) / ident['laps']

        self.logger.info('%s.%s() took %s ms' % (cls, func, ms))

    def state(self):
        return {'laps': self.laps}
