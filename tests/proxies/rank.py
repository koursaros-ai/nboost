from ...base import RouteHandler, Response, BaseServer
from ...proxies.rank import RankProxy
from ..http import HTTPTestCase
import time


class TestProxy(RankProxy):
    handler = RouteHandler(RankProxy.handler)
    search_path = '/_search'
    train_path = '/_train'

    async def magnify(self, request):
        topk = int(request.query['topk']) if 'topk' in request.query else 10
        ext_url = self.ext_url(request)
        params = dict(ext_url.query)
        params['topk'] = topk * self.multiplier
        ext_url = ext_url.with_query(params)
        return topk, request.method, ext_url, await request.read()

    async def parse(self, request, client_response):
        query = request.query['q']
        candidates = (await client_response.json())['candidates']
        return query, candidates

    async def reorder(self, client_response, topk, ranks):
        candidates = (await client_response.json())['candidates']
        reordered = [candidates[i] for i in ranks[:topk]]
        return Response.JSON_OK(dict(candidates=reordered))


class TestServer(BaseServer):
    handler = RouteHandler(BaseServer.handler)

    @handler.add_route('GET', '/_search')
    async def search(self, request):
        candidates = [str(x) for x in range(int(request.query['topk']))]
        return Response.JSON_OK(dict(candidates=candidates))

    @handler.add_route('GET', '/_train')
    async def train(self, request):
        return Response.JSON_OK(dict(msg='train'))


class TestRankProxy(HTTPTestCase):

    def setUp(self):
        self.topk = 5

        self.server = self.setUpServer(TestServer, ['--port', '54001'])
        self.proxy = self.setUpServer(TestProxy, [
            '--model', 'TestModel',
            '--ext_port', '54001',
            '--multiplier', '6'
        ])

    def test_search_and_train(self):
        # search
        params = dict(topk=self.topk, q='test query')

        proxy_res = self.get_from(self.proxy, path='/_search', params=params)
        server_res = self.get_from(self.server, path='/_search', params=params)

        self.assertTrue(proxy_res.ok)
        self.assertTrue(server_res.ok)
        self.assertEqual(
            len(proxy_res.json()['candidates']),
            len(server_res.json()['candidates'])
        )

        # train
        headers = {
            'qid': proxy_res.headers['qid'],
            'cid': str(self.topk - 1)
        }
        train_res = self.get_from(self.proxy, path='/_train', headers=headers)
        self.assertEqual(train_res.status_code, 204)

        # test status
        res = self.get_from(self.proxy, path='/status')
        self.assertTrue(res.ok)
        self.assertEqual(res.json()['multiplier'], 6)
        self.assertEqual(len(res.json()['queries']), 1)
        self.assertEqual(res.json()['search_path'], '/_search')
        self.assertEqual(res.json()['train_path'], '/_train')
        # time.sleep(30)

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
