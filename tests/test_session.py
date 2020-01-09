import unittest
from nboost.helpers import get_jsonpath, flatten
from nboost.session import Session


class TestConfigMap(unittest.TestCase):
    def test_request_1(self):
        request_1 = {
            "body": {
                "from": 0, "size": 20,
                "query": {
                    "term": {"user": "kimchy"}
                },
                "nboost": {
                    "cids": ['0', '2']
                }
            }
        }

        session = Session()
        session.request = request_1
        self.assertEqual("kimchy", session.query)
        self.assertEqual(20, session.topk)

    def test_request_2(self):
        request_2 = {
            "url": {
                "query":
                    {"q": "message:test query", "size": 20}
            }
        }

        session = Session()
        session.request = request_2
        self.assertEqual("message:test query", session.query)

    def test_request_3(self):
        request_3 = {
            "body": {
                "query": {
                    "match": "hello there"
                },
            }
        }

        session = Session()
        session.request = request_3
        self.assertEqual("hello there", session.query)

    def test_request_4(self):
        request_4 = {
            "body": {
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
        }

        session = Session(query_path='body.query.function_score.query.bool.should.[*].match.text.query')
        session.request = request_4
        self.assertEqual('query one. query two', session.query)

    def test_request_5(self):
        request_5 = {
            "body": {
                "id": "searchTemplate",
                "params": {
                    "query": "my query",
                    "from": 0,
                    "size": 9
                }
            }
        }
        session = Session(query_path='body.params.query')
        session.request = request_5
        self.assertEqual('my query', session.query)

    def test_response_1(self):
        response_1 = {
            "body": {
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
        }

        session = Session(cvalues_path='_source.message')
        session.response = response_1
        self.assertEqual(1.4, session.choices[0]['_score'])

        self.assertEqual(["trying out Elasticsearch", "second result", "third result"], session.cvalues)
        self.assertEqual(['0', '1', '2'], session.cids)










