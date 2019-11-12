from elasticsearch import Elasticsearch
from .helpers import es_bulk_index
from tutorials import RESOURCES

READ_CHUNKSIZE = 10 * 6
TIMEOUT = 10000
MAX_CHUNK_BYTES = 10 ** 9
MAX_RETRIES = 10


def another_tutorial(args):
    pass


def opensource(args):

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

    es = Elasticsearch(host=args.es_host, port=args.es_port, timeout=TIMEOUT)

    es_bulk_index(es, stream_index())

    if es.indices.exists('opensource'):
        res = es.indices.delete(index='opensource')
        print(res)
    res = es.indices.create(index='opensource', body=index)
    print(res)


def demo(args):
    pass