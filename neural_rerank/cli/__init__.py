import argparse
import sys
import termcolor
from .. import models, clients, proxy, server


def create_server(argv: list = sys.argv) -> server.BaseServer:
    parser = set_parser()
    args = parser.parse_args(argv)
    return server.BaseServer(
        host=args.host,
        port=args.port,
        verbose=args.verbose
    )


def create_client(argv: list = sys.argv) -> clients.BaseClient:
    parser = set_parser()
    args = parser.parse_args(argv)
    return getattr(clients, args.client)(
        multiplier=args.multiplier,
        field=args.field,
        verbose=args.verbose
    )


def create_model(argv: list = sys.argv) -> models.BaseModel:
    parser = set_parser()
    args = parser.parse_args(argv)
    return getattr(models, args.model)(
        lr=args.lr,
        data_dir=args.data_dir,
        verbose=args.verbose
    )


def create_proxy(argv: list = sys.argv) -> proxy.BaseProxy:
    parser = set_parser()
    args = parser.parse_args(argv)
    client = create_client(argv)
    model = create_model(argv)
    return proxy.BaseProxy(
        model=model,
        client=client,
        host=args.host,
        port=args.port,
        ext_host=args.ext_host,
        ext_port=args.ext_port,
        read_bytes=args.read_bytes,
        verbose=args.verbose
    )


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
    parser.add_argument('--ext_port', type=int, default=54001, help='port of the server')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    parser.add_argument('--field', type=str, help='specified meta field to train on')
    parser.add_argument('--lr', type=float, default=10e-3, help='learning rate of the model')
    parser.add_argument('--data_dir', type=str, default='/.cache', help='dir for model binary')
    parser.add_argument('--client', type=str, default='ESClient', help='client class to load')
    parser.add_argument('--model', type=str, default='DBERTRank', help='model class to load')
    parser.add_argument('--read_bytes', type=int, default=2048, help='chunk size to read/write')
    return parser
