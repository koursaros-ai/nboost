from ..cli import set_logger
from aiohttp import web
from typing import Mapping, Callable


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


class Base:
    _requires = []
    _state = MDict()

    def __new__(cls, verbose=False, **kwargs):
        cls.logger = set_logger(cls.__name__, verbose=verbose)
        cls._check_requires()
        cls.logger.info('\nINIT: %s%s' % (
            cls.__name__,
            cls._format_kwargs({**kwargs, 'verbose': verbose})
        ))
        cls.add_state(cls.spec)
        return super().__new__(cls)

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

    @classmethod
    def add_state(cls, f: Callable, name: str = None):
        key = name if name else f.__name__
        cls._state += {key: f}

    @property
    def state(self):
        return {k: v(self) for k, v in self._state.items()}


