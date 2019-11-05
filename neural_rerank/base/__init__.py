from ..cli import set_logger
from typing import Callable
from typing import Iterable
from pprint import pformat
from aiohttp import web
import copy
import json

DEBUG_TYPES = {
    web.BaseRequest: ['host', 'path', 'remote', 'headers', 'query', 'method'],
    web.Response: ['body', 'reason', 'status', 'headers']
}


def pfmt_obj(obj: object):
    """ cast to dict if possible then pprint format """
    try:
        obj = dict(obj)
    except (TypeError, ValueError, RuntimeError):
        pass

    try:
        obj = json.loads(obj)
    except (TypeError, json.decoder.JSONDecodeError):
        pass

    return pformat(obj)


def pfmt_attrs(obj: object, attrs: Iterable) -> str:
    """
    :param obj: python obj
    :param attrs: list of attributes to format
    :return:
        ATTR1: VALUE1
        ATTR2: VALUE2
        ...
    """
    return pfmt_obj({a: pfmt_obj(getattr(obj, a)) for a in dir(obj) if a in attrs})


def pfmt(obj: object):
    attrs = DEBUG_TYPES.get(obj.__class__, None)
    return pfmt_attrs(obj, attrs) if attrs else 'Type "%s" not registered with handler'


def running_avg(avg: float, new: float, n: int):
    return (avg * n + new) / n


class Base:
    def __init__(self, verbose=False, **kwargs):
        self.verbose = verbose
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)
        self.logger.info(pformat({**kwargs, 'verbose': verbose}))


class BaseHandler:
    def __init__(self, *handlers: 'BaseHandler'):
        self.states = set()

        for handler in handlers:
            self.states |= copy.deepcopy(handler.states)

    def add_state(self, f: Callable):
        self.states.add(f)

    def bind_states(self, b: Base) -> dict:
        return {f.__name__: f(b) for f in self.states}





