import csv, os
import requests
from elasticsearch import Elasticsearch

INDEX = 'ms_marco'
DATA_PATH = '.'

es = Elasticsearch()

def train():
    qrels = dict()
    train_set = []

    with open(os.path.join(DATA_PATH, 'qrels.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, _, doc_id, _ in data:
            qrels[doc_id] = qid
    queries = dict()

    with open(os.path.join(DATA_PATH, 'queries.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, query in data:
            queries[qid] = qid

    with open(os.path.join(DATA_PATH, 'collection.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for doc_id, passage in data:
            if doc_id in qrels:
                query = queries[qrels[doc_id]]
                res = es.search(index=INDEX, body={
                    "query": {
                        "match": {
                            "passage": {
                                "query": query
                            }
                        }
                    }
                }, filter_path=['hits.hits._*'])
                candidates = []
                labels = []
                for hit in res['hits']['hits']:
                    candidates.append(hit['_source']['passage'])
                    labels.append(1.0 if doc_id == hit['_id'] else 0.0)
                candidates.append(passage)
                labels.append(1.0)
                requests.request('POST', 'http://localhost:53001/bulk', json={
                    "query": query,
                    "candidates": labels,
                    "labels": labels
                })

def evaluate():
    pass

if __name__ == '__main__':
    train()
    evaluate()