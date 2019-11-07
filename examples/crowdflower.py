from elasticsearch import Elasticsearch, RequestsHttpConnection
from tests.paths import RESOURCES
import csv
import requests

INDEX = 'crowdflower'


def dump():
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 53001}],
        )
        for row in list(sample_data):
            es.index(
                index=INDEX,
                id=row[0],
                body=dict(title=row[2], description=row[3])
            )


def query():
    es = Elasticsearch(hosts=[{"host": "localhost", "port": 53001}])
    res = es.search(index=INDEX, body={
        "query": {
            "match": {
                "description": {
                    "query": "test"
                }
            }
        }
    })
    qid = res['qid']

def train():
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 53001}],
        )
        for row in sample_data:
            title, description, label = row[2:5]
            requests.request('POST', 'localhost:53001/bulk', data={
                "title" : title,
                "description" : description,
                "label" : label
            })


if __name__ == '__main__':
    # dump()
    # query()
    train()