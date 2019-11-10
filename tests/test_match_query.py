import unittest
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os, csv

INDEX = 'test_ms_marco'

MAPPINGS = {
    "mappings": {
        "properties": {
            "passage": {
                "type": "text",
                "analyzer": "english"
            }
        }
    }
}

def stream_bodies():
    with open(os.path.join('collection.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for id, passage in data:
            body = {
                "_index": INDEX,
                "_id": id,
                "_source": {
                    "passage": passage,
                }
            }
            if int(id) % 10000 == 0:
                print(f'Sent {id}: {passage}.')
            if id > 1000:
                break
            yield body

class TestMatchQuery(unittest.TestCase):

    def setUp(self) -> None:
        self.es = Elasticsearch(host='localhost', post=53001)
        if self.es.indices.exists(INDEX):
            res = self.es.indices.delete(index=INDEX)
        res = self.es.indices.create(index=INDEX, body=MAPPINGS)
        print('Sending articles.')
        for ok, response in elasticsearch.helpers.streaming_bulk(self.es, actions=stream_bodies()):
            if not ok:
                # failure inserting
                print(response)

    def test_match_query(self):
        res = self.es.search(index=INDEX, body={
            "size": 10,
            "query": {
                "match": {
                    "passage": {
                        "query": 'the test'
                    }
                }
            }
        }, filter_path=['hits.hits._*'])