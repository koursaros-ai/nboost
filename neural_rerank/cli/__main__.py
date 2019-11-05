from neural_rerank.cli import set_parser
from elasticsearch import Elasticsearch

from neural_rerank.clients import ESClient
from neural_rerank.models import DBERTRank
from neural_rerank.proxies import BaseProxy

proxy_cls, client_cls, server_cls = BaseProxy, ESClient, DBERTRank

if __name__ == '__main__':
    parser = set_parser()
    es = Elasticsearch()
    class MyProxy(proxy_cls, client_cls, server_cls):
        pass
    args = parser.parse_args()
    proxy = MyProxy(**vars(args))
    proxy.start()
    proxy.is_ready.wait()