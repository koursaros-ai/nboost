import requests
from unittest.case import SkipTest
from elasticsearch import Elasticsearch
from tests.paths import RESOURCES
import csv

INDEX_SIZE = 1000


def check_es_index(host, port, index):
    es = Elasticsearch()
    try:
        es_res = requests.get('http://%s:%s/%s/_stats' % (host, port, index))
    except requests.exceptions.ConnectionError:
        raise SkipTest('ES not available on port %s' % port)
    # if es_res.json()['_all']['primaries']['docs']['count'] < INDEX_SIZE:
    #     es.indices.create(index=index, ignore=400)

    # id, query, product_title, product_description, median_relevance, relevance_variance
    with RESOURCES.joinpath('train.csv').open() as fh:
        sample_data = csv.reader(fh)
        print('Dumping train.csv...')
        for row in list(sample_data)[:INDEX_SIZE]:
            es.index(
                index=index,
                id=row[0],
                body=dict(title=row[2], description=row[3])
            )

