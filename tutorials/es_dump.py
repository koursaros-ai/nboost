
import os, csv, sys
import argparse


## MS MARCO DUMP
def stream_msmarco_full(index):
    with open('collection.tsv') as fh:
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

    adf = argparse.ArgumentDefaultsHelpFormatter

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

