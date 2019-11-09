from collections import ChainMap
import termcolor
import itertools
import logging
import copy
import os


class StatefulBase:
    """ The base of each nboost component and the proxy. The role of the
    Stateful base is to return the internal state of each component by calling
    the chain_state() command."""
    def __init__(self, verbose=True, **kwargs):
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)
        # useful counter that you can call next() on
        self.counter = itertools.count()

        if kwargs:
            self.logger.critical('Unused arguments: %s' % kwargs)

    @property
    def _state(self) -> dict:
        """If a component has a defined state() method, it is chained together
        with any defined state() in it's parent classes, passing the object
        as the argument. """
        return {self.__module__: {**dict(ChainMap(
            *[getattr(cls, 'state', lambda _: {})(self) for cls in self.__class__.mro()]
        )), 'class': self.__class__.__name__}}

    def chain_state(self, other_state: dict) -> dict:
        """ Used for chaining states of multiple components together. """
        return {**self._state, **other_state}


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




