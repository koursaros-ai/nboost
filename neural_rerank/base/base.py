from ..cli import set_logger
from aiohttp import web, web_routedef
from typing import Mapping, Callable
import functools
import copy
from typing import List, Tuple


class Response:
    PLAIN_OK = lambda x: web.Response(body=x, status=200)
    JSON_OK = lambda x: web.json_response(x, status=200)
    NO_CONTENT = lambda: web.Response(status=204)
    INTERNAL_ERROR = lambda x: web.json_response(
        dict(error=str(x), type=type(x).__name__), status=500)


class MDict(dict):
    def __add__(self, other: Mapping):
        for k, v in other.items():
            if isinstance(self.get(k, k), Mapping) and isinstance(v, Mapping):
                self[k] = MDict(self[k]) + MDict(v)
            else:
                self[k] = v

        return self


class Handler:
    def __init__(self, *handlers: Tuple['Handler']):
        self.routes = []
        self.states = set()
        for handler in handlers:
            self.routes += copy.deepcopy(handler.routes)
            self.states |= copy.deepcopy(handler.states)

    def add_route(self, method: str, path: str):
        def decorator(f: Callable):
            functools.wraps(f)
            self.routes.append([method, path, f.__name__])
            return f
        return decorator

    def add_state(self):
        def decorator(f: Callable):
            functools.wraps(f)
            self.states.add(f)
            return f
        return decorator

    def get_routes(self, obj: object) -> List[web_routedef.RouteDef]:
        print(self.routes)
        return [web.route(m, p, getattr(obj, fname)) for m, p, fname in self.routes]

    def get_states(self, obj: object) -> dict:
        return {f.__name__: f(obj) for f in self.states}


class Base:
    handler = Handler()
    _requires = []
    _state = MDict()

    def __new__(cls, verbose=False, **kwargs):
        cls.logger = set_logger(cls.__name__, verbose=verbose)
        cls._check_requires()
        cls.logger.info('\nINIT: %s%s' % (
            cls.__name__,
            cls._format_kwargs({**kwargs, 'verbose': verbose})
        ))
        return super().__new__(cls)

    @handler.add_state()
    def spec(self):
        return [cls.__name__ for cls in self.__class__.mro()]

    @classmethod
    def _check_requires(cls):
        """ Makes sure that all required subclasses exist """
        if not set(cls._requires).issubset(cls.mro()):
            raise TypeError('%s requires %s subclasses, but found %s' % (
                cls.__name__, cls._requires, cls.mro()))

    @classmethod
    def _format_kwargs(cls, kwargs):
        return ''.join([cls._format_kwarg(k, v) for k, v in kwargs.items()])

    @staticmethod
    def _format_kwarg(k, v):
        switch = k[:14], ' ' * (15 - len(k)), v, v.__class__.__name__
        return '\n\t--%s%s%s (%s)' % switch


