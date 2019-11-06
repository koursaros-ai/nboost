from neural_rerank import clients
from neural_rerank import models
from neural_rerank.proxy import BaseProxy
from neural_rerank.cli import set_parser

if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()
    client = getattr(clients, args.client)(**vars(args))
    model = getattr(models, args.model)(**vars(args))
    proxy = BaseProxy(client, model, **vars(args))
    proxy.start()
    proxy.is_ready.wait()