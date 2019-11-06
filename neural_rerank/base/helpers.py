
from typing import Iterable
from pprint import pformat
from aiohttp import web
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


