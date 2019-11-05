import logging
import termcolor
import argparse
import os
import copy
import pprint
import requests
from typing import Iterable
import shutil
import json
from aiohttp import web


def format_pyobj(obj: object) -> str:
    try:
        obj = dict(obj)
    except (TypeError, ValueError, RuntimeError):
        pass

    try:
        obj = json.loads(obj)
    except (TypeError, json.decoder.JSONDecodeError):
        pass

    return pprint.pformat(obj)


def format_attrs(obj, attrs: Iterable = None) -> str:
    """

    :param obj: any python obj
    :param attrs: list of attrs you want to print (default prints all)
    :return:
        ATTR1: VALUE1
        ATTR2: VALUE2
        ...
    """
    fmt = ''
    fmt_dir = dict()
    size = shutil.get_terminal_size((80, 20))
    max_height = round(size.lines / 8)
    max_width = round(size.columns / 3 * 2)

    for key in dir(obj):
        if not attrs or key in attrs:
            try:
                attr = getattr(obj, key)
            except AssertionError:
                continue

            fmt_dir[key] = format_pyobj(attr).split('\n')

    for attr in fmt_dir:
        lines = fmt_dir[attr]
        lines = lines[:max_height] + ['...'] if len(lines) >= max_height else lines
        lines = [attr + ': ' + lines[0]] + [' ' * len(attr) + line for line in lines[1:]]
        lines = [line[:max_width] + '...' if len(line) > max_width else line for line in lines]

        fmt += '\n' + '\n'.join(lines)

    return fmt


def format_response(response: requests.models.Response):
    attrs = ['url', 'status_code', 'reason', 'headers', 'content']
    return format_attrs(response, attrs=attrs)


async def format_async_response(response: web.Response):
    attrs = ['body', 'reason', 'status', 'headers']
    return format_attrs(response, attrs=attrs)


async def format_async_request(response: web.BaseRequest):
    attrs = ['host', 'path', 'remote', 'headers', 'query', 'method']
    return format_attrs(response, attrs=attrs)


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
