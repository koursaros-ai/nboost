from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os, csv

## MS MARCO DUMP
INDEX = 'ms_marco'

ES_HOST = '35.238.60.182'
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
            "number_of_shards": 5
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
            yield body


if __name__ == "__main__":
    es = Elasticsearch(host=ES_HOST,timeout=REQUEST_TIMEOUT)

    if es.indices.exists(INDEX):
        res = es.indices.delete(index=INDEX)
        print(res)
    res = es.indices.create(index=INDEX, body=MAPPINGS)

    print('Sending articles.')
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=stream_bodies()):
        if not ok:
            # failure inserting
            print(response)