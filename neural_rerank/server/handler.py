from ..base import BaseHandler
from typing import Callable
from aiohttp import web_routedef
from typing import List
from aiohttp import web
import copy


class ServerHandler(BaseHandler):
    def __init__(self, *handlers: 'ServerHandler'):
        super().__init__(*handlers)
        self.routes = {}

        for handler in handlers:
            self.routes.update(copy.deepcopy(handler.routes))

    def add_route(self, method: str, path: str):
        def wrap(f: Callable):
            self.routes[path] = dict(
                method=method,
                func=f.__name__,
                lat=float(),
                reqs=int()
            )
            return f
        return wrap

    def bind_routes(self, proxy) -> List[web_routedef.RouteDef]:
        # import json
        # print(proxy.__class__.__name__, json.dumps(self.routes, indent=4))
        return [web.route(
            self.routes[path]['method'],
            path,
            getattr(proxy, self.routes[path]['func'])
        ) for path in self.routes]

