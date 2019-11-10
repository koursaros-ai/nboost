import csv, os
import requests
from elasticsearch import Elasticsearch
from collections import defaultdict
import time

INDEX = 'ms_marco'
ES_HOST = '35.238.60.182'
ES_PORT = 9200
# ES_HOST = 'localhost'
# ES_PORT = 53001
DATA_PATH = '.'
TOPK = 1000
REQUEST_TIMEOUT = 10000

# es = Elasticsearch(host=ES_HOST)
es = Elasticsearch(host=ES_HOST,port=ES_PORT,timeout=REQUEST_TIMEOUT)


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
            # query_id = res['qid']
            qid_hits = defaultdict(lambda: (0, TOPK+1))
            candidates = []
            labels = []
            cids = []
            for rank, hit in enumerate(res['hits']['hits']):
                if (qid, hit['_id']) in qrels:
                    count, min_rank = qid_hits[qid]
                    qid_hits[qid] = (count + 1, min(min_rank, rank+1))
                    candidates.append(hit['_source']['passage'])
                    labels.append(1.0 if doc_id == hit['_id'] else 0.0)
                    # cids.append(hit['cid'])
            hits += qid_hits[qid][0]
            total += qid_count[qid]
            # if qid_hits[qid][0] > 0:
            #     timeit(requests.request, 'POST', 'http://localhost:53001/train', json={
            #         "qid": query_id,
            #         "cids": cids
            #     })
            if qid_hits[qid][1] < TOPK + 1:
                mrr += (1/qid_hits[qid][1])
            if total > 0:
                print("recall @ top %s: %s ." % (TOPK, hits/total), "MRR: %s " % (mrr/total))
            # print("hits: %s, avg rank: %s " % qid_hits[qid], " total: %s" % qid_count[qid])

def evaluate():
    pass

if __name__ == '__main__':
    # es_latency()
    train()
    # evaluate()