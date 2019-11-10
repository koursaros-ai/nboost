from nboost.paths import RESOURCES
from nboost.codex import ESCodex
from nboost.base.types import *
import json as JSON
import unittest


class TestESCodex(unittest.TestCase):
    def test_es_codex(self):
        codex = ESCodex(multiplier=5, field='message')
        query_json = RESOURCES.joinpath('es_query.json').read_bytes()
        result_json = RESOURCES.joinpath('es_result.json').read_bytes()
        method = 'GET'
        path = '/test/_search'
        headers = {'Content-Length': 250}
        query_params = {'q': 'message:this is a test', 'size': 20}
        ranks = Ranks([1, 0, 2])
        qid = Qid(5)
        cids = [Cid(1), Cid(2), Cid(3)]

        query_req = Request(method, path, headers, query_params, b'')
        topk = codex.topk(query_req)
        self.assertEqual(topk, 20)

        query_mreq = codex.magnify(query_req, topk)
        self.assertEqual(query_mreq.params['size'], 100)

        json_req = Request(method, path, headers, {}, query_json)
        json_mreq = codex.magnify(json_req, topk)
        self.assertEqual(JSON.loads(json_mreq.body)['size'], 100)

        query_mres = Response({}, result_json, 200)
        query, choices = codex.parse(query_mreq, query_mres)
        self.assertEqual(query, b'this is a test')
        self.assertEqual(choices[0], b'trying out Elasticsearch')

        r = codex.pack(topk, query_mres, query, choices, ranks, qid, cids)
        self.assertNotIn('Content-Length', r.headers)

        train_req = Request('POST', '/train', {}, {'qid': 10, 'cid': 20}, b'')
        qid, cids = codex.pluck(train_req)
        self.assertEqual(qid, 10)
        self.assertEqual(cids, [20])

        err = codex.catch(ValueError('This is an exception'))
        self.assertEqual(err.status, 500)

