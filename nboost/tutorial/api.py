from elasticsearch import Elasticsearch
from .helpers import es_bulk_index
from nboost.tutorial import RESOURCES


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

    es = Elasticsearch(host=args.host, port=args.port, timeout=10000)

    if es.indices.exists('opensource'):
        res = es.indices.delete(index='opensource')
        print('Deleting opensource index')
        print(res)
    print('Creating opensource index on %s:%s' % (args.host, args.port))
    res = es.indices.create(index='opensource', body=index)
    print(res)

    print('Indexing opensource.txt')
    es_bulk_index(es, stream_index())