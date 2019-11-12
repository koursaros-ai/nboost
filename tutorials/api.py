from elasticsearch import Elasticsearch
from .helpers import es_bulk_index
from tutorials import RESOURCES


def another_tutorial(args):
    pass


def opensource(args):
    """Creates an "opensource" elasticsearch index from opensource.txt"""

    mappings = {"properties": {"passage": {"type": "text"}}}
    settings = {"index": {"number_of_shards": 5, "number_of_replicas": 0}}
    index = dict(mappings=mappings, settings=settings)

    def stream_index():
        with RESOURCES.joinpath('opensource.txt').open() as fh:
            for passage in fh:
                body = {
                    "_index": 'opensource',
                    "_source": {
                        "passage": passage,
                    }
                }
                yield body

    es = Elasticsearch(host=args.es_host, port=args.es_port, timeout=10000)

    if es.indices.exists('opensource'):
        res = es.indices.delete(index='opensource')
        print(res)
    res = es.indices.create(index='opensource', body=index)
    print(res)

    es_bulk_index(es, stream_index())