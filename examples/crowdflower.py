from elasticsearch import Elasticsearch, RequestsHttpConnection
from tests.paths import RESOURCES
import csv

INDEX = 'crowdflower'


def dump():
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        print('Dumping train.csv...')
        es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 53001}],
            # connection_class=RequestsHttpConnection
        )
        for row in list(sample_data):
            es.index(
                index=INDEX,
                id=row[0],
                body=dict(title=row[2], description=row[3])
            )


def main():
    es = Elasticsearch(hosts=[{"host": "localhost", "port": 9200}])
    res = es.search(index=INDEX, body={
        "query": {
            "match": {
                "description": {
                    "query": "test"
                }
            }
        }
    })
    print(res)


if __name__ == '__main__':
    # dump()
    main()