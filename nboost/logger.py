"""Logger for NBoost classes"""

import termcolor
import logging
import copy
import os


def set_logger(context, verbose=False):
    """Return colored logger with specified context name and debug=verbose"""
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
    """Windows support for logger"""
    def __init__(self, context, verbose):
        self.context = context
        self.verbose = verbose
        self.info = self.format_msg('I:%s:%s')
        self.debug = self.format_msg('D:%s:%s')
        self.error = self.format_msg('E:%s:%s')
        self.warning = self.format_msg('W:%s:%s')

    def format_msg(self, string_format: str):
        """Format incoming logging messages with a given format"""
        def func(msg: str, **_):
            """Function to replace incoming stream"""
            print(string_format % (self.context, msg), flush=True)
        return func


class ColoredFormatter(logging.Formatter):
    """Format log levels with color"""
    MAPPING = {
        'DEBUG': dict(color='green', on_color=None),
        'INFO': dict(color='cyan', on_color=None),
        'WARNING': dict(color='yellow', on_color=None),
        'ERROR': dict(color='grey', on_color='on_red'),
        'CRITICAL': dict(color='grey', on_color='on_blue'),
    }

    PREFIX = '\033['
    SUFFIX = '\033[0m'

    def format(self, record):
        """Add log ansi colors"""
        crecord = copy.copy(record)
        seq = self.MAPPING.get(crecord.levelname, self.MAPPING['INFO'])
        crecord.msg = termcolor.colored(crecord.msg, **seq)
        return super().format(crecord)
