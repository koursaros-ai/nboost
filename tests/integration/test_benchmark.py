import requests, csv
from collections import defaultdict


with open('qrels.dev.small.tsv') as file:
    qid_map = defaultdict(list)
    for qid, _, cid, _ in csv.reader(file, delimiter='\t'):
        qid_map[qid].append(cid)

with open('queries.dev.small.tsv') as file:
    for qid, query in csv.reader(file, delimiter='\t'):
        cids = qid_map[qid]
        print(requests.post(
            url='http://localhost:8000/ms_marco/_search',
            json={
                'nboost': {
                    'rerank_cids': cids,
                }
            },
            params={
              'q': query,
            }
        ).json())