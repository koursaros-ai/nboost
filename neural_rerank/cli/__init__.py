import logging
import termcolor
import argparse
import os
import copy
import sys
from .. import models, clients, proxy, server


def create_server(argv: list = sys.argv):
    parser = set_parser()
    args = parser.parse_args(argv)
    return server.BaseServer(
        verbose=args.verbose,
        host=args.host,
        port=args.port
    )


def create_proxy(argv: list = sys.argv):
    parser = set_parser()
    args = parser.parse_args(argv)
    client = getattr(clients, args.client)(
        verbose=args.verbose,
        multiplier=args.multiplier
    )
    model = getattr(models, args.model)(
        verbose=args.verbose,
        lr=args.lr,
        data_dir=args.data_dir
    )
    return proxy.BaseProxy(
        verbose=args.verbose,
        model=model,
        client=client,
        host=args.host,
        port=args.port,
        ext_host=args.ext_host,
        ext_port=args.ext_port,
        field=args.field,
        read_bytes=args.read_bytes
    )


def set_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
            termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--ext_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--ext_port', type=int, default=54001, help='port of the server')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    parser.add_argument('--field', type=str, help='specified meta field to train on')
    parser.add_argument('--lr', type=float, default=10e-3, help='learning rate of the model')
    parser.add_argument('--data_dir', type=str, default='/.cache', help='dir for model binary')
    parser.add_argument('--client', type=str, default='ESClient', help='client class to load')
    parser.add_argument('--model', type=str, default='DBERTRank', help='model class to load')
    parser.add_argument('--read_bytes', type=int, default=2048, help='chunk size to read/write')
    return parser


class ColoredFormatter(logging.Formatter):
    MAPPING = {
        'DEBUG': dict(color='green', on_color=None),
        'INFO': dict(color='cyan', on_color=None),
        'WARNING': dict(color='yellow', on_color='on_grey'),
        'ERROR': dict(color='grey', on_color='on_red'),
        'CRITICAL': dict(color='grey', on_color='on_blue'),
    }

    PREFIX = '\033['
    SUFFIX = '\033[0m'

    def format(self, record):
        cr = copy.copy(record)
        seq = self.MAPPING.get(cr.levelname, self.MAPPING['INFO'])  # default white
        cr.msg = termcolor.colored(cr.msg, **seq)
        return super().format(cr)


def set_logger(context, verbose=False):
    if os.name == 'nt':  # for Windows
        return NTLogger(context, verbose)

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(context)
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        formatter = ColoredFormatter(
            '%(levelname)-.1s:' + context +
            ':[%(filename).3s:%(funcName).3s:%(lineno)3d]:%(message)s',
            datefmt='%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(console_handler)

    return logger


class NTLogger:
    def __init__(self, context, verbose):
        self.context = context
        self.verbose = verbose

    def info(self, msg, **kwargs):
        print('I:%s:%s' % (self.context, msg), flush=True)

    def debug(self, msg, **kwargs):
        if self.verbose:
            print('D:%s:%s' % (self.context, msg), flush=True)

    def error(self, msg, **kwargs):
        print('E:%s:%s' % (self.context, msg), flush=True)

    def warning(self, msg, **kwargs):
        print('W:%s:%s' % (self.context, msg), flush=True)
