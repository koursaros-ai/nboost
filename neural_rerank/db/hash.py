from .base import BaseDb
from ..base.types import Qid, Cid
import hashlib


class HashDb(BaseDb):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queries = dict()
        self.choices = dict()
        self.laps = dict()

        # maps query ids => [choice ids]
        self.map = dict()

    def save(self, query, choices):
        qid = next(self.counter)
        cids = []

        for choice in choices:
            cid = int(hashlib.sha1(choice).hexdigest(), 16) % (10 ** 8)
            cids.append(cid)
            self.choices[cid] = choice

        self.queries[qid] = query
        self.map[qid] = cids

        return Qid(qid), [Cid(cid) for cid in cids]

    def get(self, qid, cids):
        query = self.queries[qid]
        choices = []
        labels = []

        cids = self.map[qid]
        for _cid in cids:
            choices.append(self.choices[_cid])
            labels.append(1.0 if _cid in cids else 0.0)

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
