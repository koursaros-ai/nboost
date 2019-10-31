

from .base import BaseProxy, route_handler


class RankProxy(BaseProxy):
    @route_handler
    async def status(self, request):
        return dict(res='Chillin')

    @route_handler
    async def query(self, request):
        response, query, candidates, topk = await self.client.query(request)
        ranks = self.model.rank(query, candidates)
        qid = next(self.counter)
        self.queries[qid] = query, candidates
        return self.client.reorder(response, ranks, topk)

    @route_handler
    async def train(self, request):
        qid = int(request.query['qid'])
        cid = int(request.query['cid'])

        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1
        self.model.train(query, candidates, labels)
        return {}

