from neural_rerank import clients
from neural_rerank import models
from neural_rerank.cli import create_proxy
import sys

if __name__ == '__main__':
    proxy = create_proxy(client_cls=clients.ESClient, model_cls=models.DBERTRank)
    proxy.start()
    proxy.is_ready.wait()