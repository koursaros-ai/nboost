from ..base import BaseProxy
from aiohttp import web


class RankProxy(BaseProxy):
    routes = web.RouteTableDef()

    async def status(self, request):
        return dict(res='Chillin')

    @routes.get('/query')
    async def query(self, request):
        response, query, candidates, topk = await self.model.query(request)
        ranks = self.model.rank(query, candidates)
        qid = next(self.counter)
        self.queries[qid] = query, candidates
        return self.model.reorder(response, ranks, topk)

    @routes.get('/train')
    async def train(self, request):
        qid = int(request.query['qid'])
        cid = int(request.query['cid'])

        query, candidates = self.queries[qid]
        labels = [0] * len(candidates)
        labels[cid] = 1
        self.model.train(query, candidates, labels)
        return {}

