from ..base import *
from aiohttp import web_routedef
from typing import List, Union
import time


class ProxyHandler(BaseHandler):
    def __init__(self, *handlers: 'ProxyHandler'):
        super().__init__(*handlers)
        self.routes = {}

        for handler in handlers:
            self.routes.update(handler.routes)

    def add_route(self, method: str, path: str):
        def wrap(f: Callable):
            self.routes[path] = dict(
                method=method,
                path=path,
                func=f.__name__,
                lat=float(),
                reqs=int()
            )

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
        return [web.route(
            self.routes[path]['method'],
            path,
            getattr(proxy, self.routes[path]['func'])
        ) for path in self.routes]

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