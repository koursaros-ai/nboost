
from aiohttp import web
from typing import Union
from typing import Callable
import copy


class BaseHandler:
    def __init__(self, *handlers: 'BaseHandler'):
        self.states = set()

        for handler in handlers:
            self.states |= copy.deepcopy(handler.states)

    @staticmethod
    def plain_ok(body: bytes):
        return web.Response(body=body, status=200)

    @staticmethod
    def json_ok(body: Union[dict, list]):
        return web.json_response(body, status=200)

    @staticmethod
    def no_content():
        return web.Response(status=204)

    @staticmethod
    def redirect(url):
        raise web.HTTPTemporaryRedirect(url)

    @staticmethod
    def internal_error(body):
        return web.json_response(dict(error=str(body), type=type(body).__name__), status=500)

    def add_state(self, f: Callable) -> None:
        self.states.add(f)

    def bind_states(self, s: 'BaseLogger') -> dict:
        return {f.__name__: f(s) for f in self.states}


