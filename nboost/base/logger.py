import termcolor
import logging
import copy
import os


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




