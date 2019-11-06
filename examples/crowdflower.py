from elasticsearch import Elasticsearch, RequestsHttpConnection
from tests.paths import RESOURCES
import csv

INDEX = 'crowdflower'


def main():
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        print('Dumping train.csv...')
        es = Elasticsearch(
            hosts=[{"host": "localhost", "port": 53001}],
            connection_class=RequestsHttpConnection
        )
        for row in list(sample_data):
            es.index(
                index=INDEX,
                id=row[0],
                body=dict(title=row[2], description=row[3])
            )


if __name__ == '__main__':
    main()