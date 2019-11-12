from elasticsearch import Elasticsearch
from collections import defaultdict
import time

INDEX = 'ms_marco'
ES_HOST = '35.238.60.182'
ES_PORT = 9200

def generate_subset(topic, size, output_file):
    es = Elasticsearch(host=ES_HOST,port=ES_PORT)
    res = es.search(index=INDEX, body={
        "size": size,
        "query": {
            "match": {
                "passage": {
                    "query": topic
                }
            }
        }
    }, filter_path=['hits.hits._*'])
    with open(output_file, 'w') as out:
        for rank, hit in enumerate(res['hits']['hits']):
            out.write(hit['_source']['passage'] + '\n')


if __name__=='__main__':
    main()