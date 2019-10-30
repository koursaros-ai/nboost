import logging
import termcolor
import argparse
import os


def set_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
                        termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--client', type=str, default='BaseClient', help='which client to use')
    parser.add_argument('--model', type=str, default='BaseModel', help='which model to use')
    parser.add_argument('--server_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--server_port', type=int, default=9200, help='port of the server')
    parser.add_argument('--proxy_host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--proxy_port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    return parser


def set_logger(context, verbose=False):
    if os.name == 'nt':  # for Windows
        return NTLogger(context, verbose)

    logger = logging.getLogger(context)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter(
        '%(levelname)-.1s:' + context + ':[%(filename).3s:%(funcName).3s:%(lineno)3d]:%(message)s', datefmt=
        '%m-%d %H:%M:%S')
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