FAKE_ES_DATA = {
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
            "value": 4,
            "relation": "eq"
        },
        "max_score": 1.3862944,
        "hits": [
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "0",
                "_score": 1.3862944,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "trying out Elasticsearch",
                    "user": "kimchy"
                }
            },
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "1",
                "_score": 1.352342,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 2,
                    "message": "oooo kimchy is great",
                    "user": "kimchy"
                }
            },
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "2",
                "_score": 1.2342,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "jk kimchy is nasty",
                    "user": "kimchy"
                }
            },
            {
                "_index": "twitter",
                "_type": "_doc",
                "_id": "3",
                "_score": 1.1111,
                "_source": {
                    "date": "2009-11-15T14:12:12",
                    "likes": 0,
                    "message": "what the heck even is kimchy",
                    "user": "kimchy"
                }
            }
        ]
    }
}
