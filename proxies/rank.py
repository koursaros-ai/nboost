

from .base import BaseProxy


class RankProxy(BaseProxy):
    async def status(self):
        return dict(res='Chillin')

    async def query(self, request):
        response, query, candidates, topk = await self.client.query(request)
        ranks = self.model.rank(query, candidates, topk)
        qid = next(self.counter)
        self.queries[qid] = query, candidates
        return self.client.reorder(response, ranks)

    async def train(self, request):
        qid = int(request.query['qid'])
        cid = int(request.query['cid'])

        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1
        return self.model.train(query, candidates, labels)

