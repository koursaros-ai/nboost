from nboost.model.test import TestModel
from nboost.codex.es import ESCodex
from nboost.base.types import *
import json as JSON
import unittest
from tests import RESOURCES


class TestESCodex(unittest.TestCase):
    def test_es_codex(self):
        codex = ESCodex(multiplier=5, field='message')
        query_json = RESOURCES.joinpath('es_query.json').read_bytes()
        result_json = RESOURCES.joinpath('es_result.json').read_bytes()
        method = b'GET'
        path = b'/test/_search'
        params = {b'q': b'message:this is a test', b'size': 20}
        version = b'HTTP/1.1'
        headers = {b'Content-Length': b'250'}
        qid = Qid(5)
        cids = [Cid(1), Cid(2), Cid(3)]

        query_req = Request(method, path, params, version, headers, b'')
        topk = codex.topk(query_req)
        self.assertEqual(topk, 20)

        codex.magnify(query_req, topk)
        self.assertEqual(query_req.params[b'size'], b'100')

        json_req = Request(method, path, {}, version, headers, query_json)
        codex.magnify(json_req, topk)
        self.assertEqual(JSON.loads(json_req.body)['size'], 100)

        query_res = Response(version, 200, headers, result_json)
        query, choices = codex.parse(query_req, query_res)
        self.assertEqual(query.body, b'this is a test')
        self.assertEqual(choices[0].body, b'trying out Elasticsearch')

        TestModel().rank(query, choices)
        query.ident = b'10'
        codex.pack(topk, query_res, query, choices)

        train_req = Request(b'POST', b'/train', {b'_nboost': b'10', b'_id': b'20'}, version, {}, b'')
        qid, cids = codex.pluck(train_req)
        self.assertEqual(qid, b'10')
        self.assertEqual(cids, [b'20'])

        err = codex.catch(ValueError('This is an exception'))
        self.assertEqual(err.status, 500)

    def test_match_burger(self):
        response_body = RESOURCES.joinpath('match_query_res.json').read_bytes()
        response_headers = {b'Content-Length': str(len(response_body)).encode()}
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
        method = b'GET'
        path = b'/test/_search'
        headers = {b'Content-Length': str(len(request_body)).encode()}
        json_req = Request(method, path, {}, b'HTTP/1.1', headers, request_body)
        codex = ESCodex(multiplier=5, field='passage')
        res = Response(b'HTTP/1.1', 200, response_headers, response_body)
        query, choices = codex.parse(json_req, res)
        self.assertEqual(query.body, b"this is a test")
        self.assertEqual(len(choices), 100)

