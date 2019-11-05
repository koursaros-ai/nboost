from elasticsearch import Elasticsearch

from neural_rerank.clients import ESClient
from neural_rerank.models import DBERTRank
from neural_rerank.proxies import BaseProxy
from neural_rerank.cli import set_parser

proxy_cls, client_cls, server_cls = BaseProxy, ESClient, DBERTRank

if __name__ == '__main__':
    parser = set_parser()
    es = Elasticsearch()
    args = parser.parse_args()
    client = ESClient(**vars(args))
    model = DBERTRank(**vars(args))
    proxy = BaseProxy(client, model, **vars(args))
    proxy.start()
    proxy.is_ready.wait()