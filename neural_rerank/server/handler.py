from ..base import BaseHandler, pfmt
import time
import json
from typing import Callable
import functools
from aiohttp import web_routedef
from typing import List
from aiohttp import web


def running_avg(avg: float, new: float, n: int):
    return (avg * n + new) / n


class ServerHandler(BaseHandler):
    def __init__(self, *handlers: 'ServerHandler'):
        super().__init__(*handlers)
        self.routes = {}

        for handler in handlers:
            self.routes.update(handler.routes)

    def add_route(self, method: str, path: str):
        def wrap(f: Callable):
            self.routes[path] = dict(
                method=method,
                func=f.__name__,
                lat=float(),
                reqs=int()
            )
            @functools.wraps(f)
            async def decorator(proxy, req):
                proxy.logger.info('RECV: %s' % req)
                proxy.logger.debug(pfmt(req))
                self.routes[path]['reqs'] += 1
                start = time.time()
                res = await f(proxy, req)
                self.routes['lat'] = running_avg(
                    self.routes['lat'],
                    time.time() - start,
                    self.routes['reqs']
                )
                proxy.logger.info('SEND: %s' % res)
                proxy.logger.debug(pfmt(req))
                return res
            return decorator
        return wrap

    def bind_routes(self, proxy) -> List[web_routedef.RouteDef]:
        print(proxy.__class__.__name__, json.dumps(self.routes, indent=4))
        return [web.route(
            self.routes[path]['method'],
            path,
            getattr(proxy, self.routes[path]['func'])
        ) for path in self.routes]

