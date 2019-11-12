from elasticsearch import Elasticsearch
import elasticsearch.helpers
from typing import Generator


def es_bulk_index(es: Elasticsearch, g: Generator):
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=g):
        if not ok:
            # failure inserting
            print(response)
