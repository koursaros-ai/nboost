import unittest
from nboost.helpers import get_jsonpath
from nboost.maps import CONFIG_MAP


class TestConfigMap(unittest.TestCase):
    def test_request_1(self):
        config = CONFIG_MAP['elasticsearch']

        queries = get_jsonpath(REQUEST_1, config['query_path'])
        self.assertEqual("kimchy", queries[0])

        topks = get_jsonpath(REQUEST_1, config['topk_path'])
        self.assertEqual(20, topks[0])

        true_cids = get_jsonpath(REQUEST_1, config['true_cids_path'])
        self.assertEqual(['0', '2'], true_cids[0])

    def test_request_2(self):
        config = CONFIG_MAP['elasticsearch']

        queries = get_jsonpath(REQUEST_2, config['query_path'])
        self.assertEqual("message:test query", queries[0])

    def test_request_3(self):
        config = CONFIG_MAP['elasticsearch']

        queries = get_jsonpath(REQUEST_3, config['query_path'])
        self.assertEqual("hello there", queries[0])

    def test_request_4(self):
        queries = get_jsonpath(REQUEST_4, 'body.query.function_score.query.bool.should.[*].match.text.query')
        self.assertEqual(['query one', 'query two'], queries)

    def test_request_5(self):
        queries = get_jsonpath(REQUEST_5, 'body.params.query')
        self.assertEqual(['my query'], queries)

    def test_response_1(self):
        config = CONFIG_MAP['elasticsearch']

        choices = get_jsonpath(RESPONSE_1, config['choices_path'])
        self.assertEqual(1.4, choices[0][0]['_score'])

        cvalues = get_jsonpath(RESPONSE_1, config['cvalues_path'])
        self.assertEqual(["trying out Elasticsearch", "second result", "third result"], cvalues)

        cids = get_jsonpath(RESPONSE_1, config['cids_path'])
        self.assertEqual(['0', '1', '2'], cids)


REQUEST_1 = {
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

REQUEST_2 = {
    "url": {
        "query":
            {"q": "message:test query", "size": 20}
    }
}

REQUEST_3 = {
    "body": {
        "query": {
            "match": "hello there"
        },
    }
}

REQUEST_4 = {
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

REQUEST_5 = {
    "body": {
        "id": "searchTemplate",
        "params": {
            "query": "my query",
            "from": 0,
            "size": 9
        }
    }
}

RESPONSE_1 = {
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
