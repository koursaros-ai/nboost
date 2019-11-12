from elasticsearch import Elasticsearch
import elasticsearch.helpers
import os, csv, sys
import argparse

## MS MARCO DUMP

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


def stream_msmarco_full(index):
    with open(os.path.join('collection.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for id, passage in data:
            body = {
                "_index": index,
                "_id": id,
                "_source": {
                    "passage": passage,
                }
            }
            if int(id) % 10000 == 0:
                print(f'Sent {id}: {passage}.')
            yield body


def stream_subset(index):
    with open('tutorial_subset.txt') as data:
        for passage in data:
            body = {
                "_index": index,
                "_source": {
                    "passage": passage,
                }
            }
            yield body


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dump to elasticsearch')
    parser.add_argument('--task', required=True)
    parser.add_argument('--es_host', default='localhost')
    parser.add_argument('--es_port', default=9200)
    args = parser.parse_args()
    if args.task == 'ms_marco':
        action = stream_msmarco_full
    elif args.task == 'demo':
        action = stream_subset
    else:
        raise NotImplementedError('Available tasks are ms_marco and demo')

    es = Elasticsearch(host=args.es_host, port=args.es_port, timeout=REQUEST_TIMEOUT)

    if es.indices.exists(args.task):
        res = es.indices.delete(index=args.task)
        print(res)
    res = es.indices.create(index=args.task, body=MAPPINGS)

    print('Sending articles.')
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=action(args.task)):
        if not ok:
            # failure inserting
            print(response)