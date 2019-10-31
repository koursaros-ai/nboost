

from .base import BaseProxy


class RankProxy(BaseProxy):
    @property
    def status(self):
        return dict(res='Chillin')

    @route_handler
    async def status(self):
        return self.status

    @route_handler
    async def query(self, request):
        response, candidates, q = await self.client.query(request)
        ranks = self.model(q, candidates)
        self.queries[next(counter)] = q, candidates
        return client.reorder(response, ranks)

    @route_handler
    async def train(self, request):
        q, candidates = self.queries[request.query.qid]
        labels = [0] * len(candidates)
        labels[request.query.cid] = 1
        return model(q, candidates, labels=labels)



    def run(self):
        self.create_site()

