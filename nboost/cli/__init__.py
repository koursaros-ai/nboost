import argparse
import sys
import termcolor
from .. import model, server, codex, db
from ..proxy import Proxy
from typing import List


def create_proxy(argv: List[str] = sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
            termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--ext_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--ext_port', type=int, default=9200, help='port of the server')
    parser.add_argument('--lr', type=float, default=10e-3, help='learning rate of the model')
    parser.add_argument('--model_ckpt', type=str, default='marco_bert', help='path of transformers model or pretrained')
    parser.add_argument('--data_dir', type=str, default='/.cache', help='dir for model binary')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    parser.add_argument('--field', type=str, help='specified meta field to train on')
    parser.add_argument('--server', type=lambda x: getattr(server, x), default='AioHttpServer', help='server class')
    parser.add_argument('--codex', type=lambda x: getattr(codex, x), default='ESCodex', help='codex class')
    parser.add_argument('--model', type=lambda x: getattr(model, x), default='TransformersModel', help='model class')
    parser.add_argument('--db', type=lambda x: getattr(db, x), default='HashDb', help='db class')
    args = parser.parse_args(argv)
    return Proxy(**vars(args))
