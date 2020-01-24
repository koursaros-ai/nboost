import unittest
from nboost.delegates import RequestDelegate, ResponseDelegate


class TestDelegates(unittest.TestCase):
    def test_request_1(self):
        request = RequestDelegate({
            'body': {
                "from": 0,
                "size": 20,
                "query": {
                    "term": {"user": "kimchy"}
                },
                "nboost": {
                    "cids": ['0', '2']
                }
            }
        })

        self.assertEqual("kimchy", request.query)
        self.assertEqual(20, request.topk)

    def test_request_2(self):
        request = RequestDelegate({
            'url': {
                "query": {"q": "message:test query", "size": 20}
            }
        })
        self.assertEqual("message:test query", request.query)

    def test_request_3(self):
        request = RequestDelegate({
            'body': {
                "query": {
                    "match": "hello there"
                },
            }
        })

        self.assertEqual("hello there", request.query)

    def test_request_4(self):
        request = RequestDelegate({
            'body': {
                "size": 11,
                "query": {
                    "function_score": {
                        "query": {
                            "bool": {
                                "should": [
                                    {
                                        "match": {
                                            "text": {
                                                "query": "query one",
                                                "operator": "and"
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "text": {
                                                "query": "query two",
                                                "operator": "or"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        "script_score": {
                            "script": {
                                "source": "1 + ((5 - doc[\"priority\"].value) / 10.0) + ((doc[\"branch\"].value == \"All\") ? 0.5 : 0)"
                            }
                        }
                    }
                }
            }
        },
        query_path='body.query.function_score.query.bool.should.[*].match.text.query'
        )

        self.assertEqual('query one. query two', request.query)

    def test_request_5(self):
        request = RequestDelegate({
            'body': {
                "id": "searchTemplate",
                "params": {
                    "query": "my query",
                    "from": 0,
                    "size": 9
                }
            }
        },
        query_path='body.params.query'
        )
        self.assertEqual('my query', request.query)

    def test_response_1(self):
        response = ResponseDelegate({
            'body': {
                "nboost": {'cvalues_path': '_source.message'},
                "took": 5,
                "timed_out": False,
                "_shards": {
                    "total": 1,
                    "successful": 1,
                    "skipped": 0,
                    "failed": 0
                },
                "hits": {
                    "total": {
                        "value": 1,
                        "relation": "eq"
                    },
                    "max_score": 1.3862944,
                    "hits": [
                        {
                            "_index": "twitter",
                            "_type": "_doc",
                            "_id": "0",
                            "_score": 1.4,
                            "_source": {
                                "message": "trying out Elasticsearch",
                            }
                        }, {
                            "_index": "twitter",
                            "_type": "_doc",
                            "_id": "1",
                            "_score": 1.34245,
                            "_source": {
                                "message": "second result",
                            }
                        },
                        {
                            "_index": "twitter",
                            "_type": "_doc",
                            "_id": "2",
                            "_score": 1.121234,
                            "_source": {
                                "message": "third result",
                            }
                        }
                    ]
                }
            }
        }, RequestDelegate({}))

        self.assertEqual(1.4, response.choices[0]['_score'])

        self.assertEqual(["trying out Elasticsearch", "second result", "third result"], response.cvalues)
        self.assertEqual(['0', '1', '2'], response.cids)










