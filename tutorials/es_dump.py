from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os, csv, sys

## MS MARCO DUMP

ES_HOST = '35.238.60.182'
ES_PORT = 9200
READ_CHUNKSIZE = 10 * 6
REQUEST_TIMEOUT = 10000
MAX_CHUNK_BYTES = 10 ** 9
MAX_RETRIES = 10

MAPPINGS = {
    "mappings": {
        "properties": {
            "passage": {
                "type": "text"
            }
        }
    },
    "settings": {
        "index": {
            "number_of_shards": 5,
            "number_of_replicas": 0
        }
    }
}


def stream_msmarco_full():
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
            yield body


def stream_subset():
    with open('tutorial_subset.txt') as data:
        for passage in data:
            body = {
                "_index": INDEX,
                "_source": {
                    "passage": passage,
                }
            }
            yield body


if __name__ == "__main__":
    if sys.argv[1] == 'ms_marco':
        action = stream_msmarco_full
        index = 'ms_marco'
    elif sys.argv[1] == 'demo':
        action = stream_subset
        index = 'demo'
    else:
        raise NotImplementedError

    es = Elasticsearch(host=ES_HOST, port=ES_PORT, timeout=REQUEST_TIMEOUT)

    if es.indices.exists(index):
        res = es.indices.delete(index=index)
        print(res)
    res = es.indices.create(index=index, body=MAPPINGS)

    print('Sending articles.')
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=action()):
        if not ok:
            # failure inserting
            print(response)