import argparse
import sys
import termcolor
from .. import model, clients, proxy, server, codex, db
from ..proxy import Proxy
from typing import List


def create_server(cls: server.BaseServer.__class__ = server.BaseServer,
                  argv: list = sys.argv) -> server.BaseServer:
    parser = set_parser()
    args = parser.parse_args(argv)
    return cls(
        host=args.host,
        port=args.port,
        verbose=args.verbose
    )


def create_client(cls: clients.BaseClient.__class__ = clients.BaseClient,
                  argv: list = sys.argv) -> clients.BaseClient:
    parser = set_parser()
    args = parser.parse_args(argv)
    return cls(
        multiplier=args.multiplier,
        field=args.field,
        ext_host=args.ext_host,
        ext_port=args.ext_port,
        verbose=args.verbose
    )


def create_model(cls: model.BaseModel.__class__ = model.BaseModel,
                 argv: list = sys.argv) -> model.BaseModel:
    parser = set_parser()
    args = parser.parse_args(argv)
    return cls(
        lr=args.lr,
        data_dir=args.data_dir,
        verbose=args.verbose
    )


def create_proxy(cls: proxy.BaseProxy.__class__ = proxy.BaseProxy,
                 client_cls: clients.BaseClient.__class__ = clients.BaseClient,
                 model_cls: model.BaseModel.__class__ = model.BaseModel,
                 argv: list = sys.argv[1:]) -> proxy.BaseProxy:
    parser = set_parser()
    args = parser.parse_args(argv)
    return cls(
        model=create_model(model_cls, argv),
        client=create_client(client_cls, argv),
        host=args.host,
        port=args.port,
        read_bytes=args.read_bytes,
        verbose=args.verbose
    )


def creat_proxy(argv: List[str] = sys.argv):
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
            termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--ext_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--ext_port', type=int, default=9200, help='port of the server')
    parser.add_argument('--read_bytes', type=int, default=2048, help='chunk size to read/write')
    parser.add_argument('--lr', type=float, default=10e-3, help='learning rate of the model')
    parser.add_argument('--data_dir', type=str, default='/.cache', help='dir for model binary')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    parser.add_argument('--field', type=str, help='specified meta field to train on')
    parser.add_argument('--server', type=lambda x: getattr(server, x), default='AioHttpServer', help='server class')
    parser.add_argument('--codex', type=lambda x: getattr(codex, x), default='ESCodex', help='codex class')
    parser.add_argument('--model', type=lambda x: getattr(model, x), default='DBERTModel', help='model class')
    parser.add_argument('--db', type=lambda x: getattr(db, x), default='HashDb', help='db class')
    args = parser.parse_args(argv)
    return Proxy(**vars(args))


def set_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
            termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--ext_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--ext_port', type=int, default=9200, help='port of the server')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    parser.add_argument('--field', type=str, help='specified meta field to train on')
    parser.add_argument('--lr', type=float, default=10e-3, help='learning rate of the model')
    parser.add_argument('--data_dir', type=str, default='/.cache', help='dir for model binary')
    parser.add_argument('--client', type=str, default='ESClient', help='client class to load')
    parser.add_argument('--model', type=str, default='DBERTRank', help='model class to load')
    parser.add_argument('--read_bytes', type=int, default=2048, help='chunk size to read/write')
    return parser
