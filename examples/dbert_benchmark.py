from nboost.model import DBERTModel
import os
import csv
DATA_PATH = '.'


def main():
    with open(os.path.join(DATA_PATH, 'qrels.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, _, doc_id, _ in data:
            qrels.add((qid, doc_id))
            qid_count[qid] += 1
    # queries = dict()

    with open(os.path.join(DATA_PATH, 'queries.train.tsv')) as fh:
        data = csv.reader(fh, delimiter='\t')
        for qid, query in data:
            pass

if __name__ == '__main__':
    main()