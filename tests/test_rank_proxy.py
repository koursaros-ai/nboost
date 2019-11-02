from ..base import RouteHandler, Response, BaseServer
from ..cli import set_parser
from ..proxies.rank import RankProxy
import unittest
import requests


class TestProxy(RankProxy):
    handler = RouteHandler(RankProxy.handler)
    search_path = '/_search'
    train_path = '/_train'

    async def magnify(self, request):
        topk = int(request.query['size']) if 'size' in request.query else 10
        ext_url = self.ext_url(request)
        params = dict(ext_url.query)
        params['size'] = topk * self.multiplier
        ext_url = ext_url.with_query(params)
        return topk, request.method, ext_url, await request.read()

    async def parse(self, request, client_response):
        query = request.query['q']
        candidates = (await client_response.json())['candidates']
        return query, candidates

    async def reorder(self, client_response, topk, ranks):
        candidates = (await client_response.json())['candidates']
        reordered = [candidates[i] for i in ranks[:topk]]
        return Response.json_200(dict(candidates=reordered))


class TestServer(BaseServer):
    handler = RouteHandler(BaseServer.handler)

    @handler.add_route('GET', '/_search')
    async def search(self, request):
        candidates = [str(x) for x in range(int(request.query['size']))]
        return Response.json_200(dict(candidates=candidates))

    @handler.add_route('GET', '/_train')
    async def train(self, request):
        return Response.json_200(dict(msg='train'))


class TestRankProxy(unittest.TestCase):

    def setUp(self):
        parser = set_parser()
        args = parser.parse_args([
            '--verbose',
            '--port', '54001'
        ])
        self.server = TestServer(**vars(args))
        self.server.start()
        self.server.is_ready.wait()

        args = parser.parse_args([
            '--verbose',
            '--model', 'TestModel',
            '--ext_port', '54001'
        ])
        # return f(**vars(p_args))
        self.proxy = TestProxy(**vars(args))
        self.proxy.start()
        self.proxy.is_ready.wait()

    def test_search_and_train(self):
        res = requests.get(self.proxy.url + '/_search?size=5&q=testing')
        self.proxy.logger.info('%s:%s' % (res.status_code, res.content))
        self.assertTrue(res.ok)
        # self.assertEqual(res.json()['msg'], 'server_response')

    def tearDown(self):
        self.server.kill()
        self.proxy.kill()
