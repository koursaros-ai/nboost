from nboost.codex import ESCodex
from nboost.base.types import *
import json as JSON
import unittest
from . import RESOURCES


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

    def test_match_burger(self):
        response_body = RESOURCES.joinpath('match_query_res.json').read_bytes()
        response_headers = {'Content-Length': len(response_body)}
        request_body = b'''
                {
                    "size": 100,
                    "query": {
                        "match" : {
                            "passage" : {
                                "query" : "this is a test"
                            }
                        }
                    }
                }
                '''
        method = 'GET'
        path = '/test/_search'
        headers = {'Content-Length': len(request_body)}
        json_req = Request(method, path, headers, {}, request_body)
        codex = ESCodex(multiplier=5, field='passage')
        query, choices = codex.parse(json_req, Response(response_headers, response_body, 200))
        self.assertEqual(query, b"this is a test")
        self.assertEqual(len(choices), 100)

