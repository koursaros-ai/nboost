from elasticsearch import Elasticsearch, RequestsHttpConnection
from tests.paths import RESOURCES
import csv
import requests
import time

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


def benchmark():
    es = Elasticsearch(hosts=[{"host": "localhost", "port": 53001}])
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        headers = next(sample_data, None)
        es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 53001}],
        )
        start = time.time()
        total = len(list(sample_data))
        relevant_res = 0
        total_res = 0
        for i, row in enumerate(sample_data):
            if i < 0.8 * total:
                continue
            query, title, description, label = row[1:5]
            res = es.search(index=INDEX, body={
                "query": {
                    "match": {
                        "description": {
                            "query": query
                        }
                    }
                }
            }, filter_path=['hits.hits._*'])
            # print(res)
            print(f'avg {(time.time() - start)/(i+1)} s/ it')


def train():
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        headers = next(sample_data, None)
        total = len(list(sample_data))
        for i, row in enumerate(sample_data):
            if i > 0.8 * total:
                continue
            query, title, description, label = row[1:5]
            requests.request('POST', 'http://localhost:53001/bulk', json={
                "query" : query,
                "candidates" : [(title + ' ' + description)[:500]],
                "labels" : [float(label)]
            })


if __name__ == '__main__':
    # dump()
    benchmark()
    # train()