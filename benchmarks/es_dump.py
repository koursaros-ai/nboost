import os, csv, sys


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


