import csv, os
import requests
from elasticsearch import Elasticsearch
from collections import defaultdict
import time

INDEX = 'ms_marco'
ES_HOST = '35.238.60.182'
DATA_PATH = '.'
TOPK = 10
REQUEST_TIMEOUT = 10000

# es = Elasticsearch(host=ES_HOST)
es = Elasticsearch(host='localhost',port=53001,timeout=REQUEST_TIMEOUT)

def timeit(fn, *args, **kwargs):
    start = time.time()
    res = fn(*args, **kwargs)
    print("took %s seconds to run %s" % (time.time() - start, fn.__name__))
    return res

def train():
    qrels = set()
    hits = 0
    total = 0
    mrr = 0
    qid_count = defaultdict(int)

    with open(os.path.join(DATA_PATH, 'qrels.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, _, doc_id, _ in data:
            qrels.add((qid, doc_id))
            qid_count[qid] += 1
    # queries = dict()

    with open(os.path.join(DATA_PATH, 'queries.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, query in data:
            res = timeit(es.search, index=INDEX, body={
                "size": TOPK,
                "query": {
                    "match": {
                        "passage": {
                            "query": query
                        }
                    }
                }
            }, filter_path=['hits.hits._*'])
            qid_hits = defaultdict(lambda: (0, TOPK+1))
            candidates = []
            labels = []
            for rank, hit in enumerate(res['hits']['hits']):
                if (qid, hit['_id']) in qrels:
                    count, min_rank = qid_hits[qid]
                    qid_hits[qid] = (count + 1, min(min_rank, rank+1))
                    candidates.append(hit['_source']['passage'])
                    labels.append(1.0 if doc_id == hit['_id'] else 0.0)
            hits += qid_hits[qid][0]
            total += qid_count[qid]
            if qid_hits[qid][0] > 0:
                timeit(requests.request, 'POST', 'http://localhost:53001/train', json={
                    "query": query,
                    "candidates": labels,
                    "labels": labels
                })
            if qid_hits[qid][1] < TOPK + 1:
                mrr += (1/qid_hits[qid][1])
            if total > 0:
                print("recall @ top %s: %s ." % (TOPK, hits/total), "MRR: %s " % (mrr/total))
            # print("hits: %s, avg rank: %s " % qid_hits[qid], " total: %s" % qid_count[qid])


# with open(os.path.join(DATA_PATH, 'collection.tsv')) as fh:
#     data = csv.reader(fh, delimiter='\t')
#     for doc_id, passage in data:
#         if doc_id in qrels:
#             query = queries[qrels[doc_id]]
#             res = es.search(index=INDEX, body={
#                 "query": {
#                     "match": {
#                         "passage": {
#                             "query": query
#                         }
#                     }
#                 }
#             }, filter_path=['hits.hits._*'])
#             candidates = []
#             labels = []
#             for hit in res['hits']['hits']:
#                 if doc_id != hit['_id']:
#                     candidates.append(hit['_source']['passage'])
#                     labels.append(1.0 if doc_id == hit['_id'] else 0.0)
#             candidates.append(passage)
#             labels.append(1.0)


def evaluate():
    pass

if __name__ == '__main__':
    train()
    evaluate()