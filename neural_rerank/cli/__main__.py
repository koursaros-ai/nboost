from elasticsearch import Elasticsearch

from neural_rerank import clients
from neural_rerank import models
from neural_rerank.proxies import BaseProxy
from neural_rerank.cli import set_parser

proxy_cls, client_cls, server_cls = BaseProxy, ESClient, DBERTRank

if __name__ == '__main__':
    parser = set_parser()
    es = Elasticsearch()
    args = parser.parse_args()
    client = getattr(clients, args.client)(**vars(args))
    model = getattr(models, args.model)(**vars(args))
    proxy = BaseProxy(client, model, **vars(args))
    proxy.start()
    proxy.is_ready.wait()