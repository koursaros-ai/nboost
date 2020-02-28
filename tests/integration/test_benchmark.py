import requests, csv

with open('queries.dev.tsv') as file:
    for query, cids in csv.reader(file, delimiter='\t'):
        requests.post(
            url='http://localhost:8000/ms_marco/_search',
            json={
                'nboost': {
                    'rerank_cids': cids.split(','),
                    'query_prep': 'lambda query: ":".join( query.split(":")[1:] )'
                }
            },
            params={
              'q': 'passage:' + query,
            }
        )