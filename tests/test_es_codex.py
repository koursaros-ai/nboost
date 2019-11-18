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
        headers = {'Content-Length': '250'}
        qid = Qid(5)
        cids = [Cid(1), Cid(2), Cid(3)]

        query_req = Request(
            path='/test/_search',
            params={'q': 'message:this is a test', 'size': 20},
            headers=headers)
        topk = codex.topk(query_req)
        self.assertEqual(topk, 20)

        codex.magnify(query_req, topk)
        self.assertEqual('100', query_req.params['size'])

        json_req = Request(headers=headers, body=query_json)
        codex.magnify(json_req, topk)
        self.assertEqual(JSON.loads(json_req.body)['size'], 100)

        query_res = Response(headers=headers, body=result_json)
        query, choices = codex.parse(query_req, query_res)
        self.assertEqual(query.body, b'this is a test')
        self.assertEqual(choices[0].body, b'trying out Elasticsearch')

        TestModel().rank(query, choices)
        query.ident = b'10'
        codex.pack(topk, query_res, query, choices)

        train_req = Request(method='POST',
                            path='/train',
                            params={'_nboost': '10', '_id': '20'})

        qid, cids = codex.pluck(train_req)
        self.assertEqual(qid, Qid(b'10'))
        self.assertEqual(cids, [Cid(b'20')])

        err = codex.catch(ValueError('This is an exception'))
        self.assertEqual(err.status, 500)

    def test_match_burger(self):
        response_body = RESOURCES.joinpath('match_query_res.json').read_bytes()
        response_headers = {'Content-Length': str(len(response_body))}
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

        headers = {'Content-Length': str(len(request_body))}
        json_req = Request(path='/test/_search', headers=headers, body=request_body)
        codex = ESCodex(multiplier=5, field='passage')
        res = Response(headers=response_headers, body=response_body)
        query, choices = codex.parse(json_req, res)
        self.assertEqual(query.body, b"this is a test")
        self.assertEqual(len(choices), 100)

