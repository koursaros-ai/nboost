from ..base import *
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
        if query.ident is None:
            query.ident = Qid(str(next(self.counter)), 'utf8')

        cids = []
        for choice in choices:
            if choice.ident is None:
                cid = Cid(hashlib.sha1(choice.body).hexdigest().encode())
                choice.ident = cid

            cids.append(choice.ident)
            self.choices[choice.ident] = choice.body

        self.queries[query.ident] = query.body
        self.map[query.ident] = cids

    def get(self, qid, cids):
        query = Query(self.queries[qid], qid)
        choices = []

        cids = self.map[qid]
        for _cid in cids:
            choices.append(Choice(self.choices[_cid], _cid))

        return query, choices

    def lap(self, ms, cls, func):

        if cls not in self.laps:
            self.laps[cls] = {func: dict(avg_ms=ms, laps=1)}
        elif func not in self.laps[cls]:
            self.laps[cls][func] = dict(avg_ms=ms, laps=1)
        else:
            f = self.laps[cls][func]
            f['avg_ms'] *= f['laps']
            f['laps'] += 1
            f['avg_ms'] += ms
            f['avg_ms'] /= f['laps']
            f['avg_ms'] = round(f['avg_ms'], 5)

        self.logger.info('%s.%s() took %s ms' % (cls, func, ms))

    def state(self):
        return {'laps': self.laps}
