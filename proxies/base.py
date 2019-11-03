from ..base import BaseServer, RouteHandler
from .. import models
from aiohttp import web
import itertools
import aiohttp


class BaseProxy(BaseServer):
    handler = RouteHandler(BaseServer.handler)

    def __init__(self, model: str = 'BaseModel', ext_host: str = '127.0.0.1',
                 ext_port: int = 53001, **kwargs):
        super().__init__(**kwargs)
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.model = getattr(models, model)(**kwargs)
        self.counter = itertools.count()
        self.queries = dict()

    def ext_url(self, request: 'web.BaseRequest'):
        return request.url.with_host(self.ext_host).with_port(self.ext_port)

    async def not_found_handler(self, request: 'web.BaseRequest'):
        ext_url = self.ext_url(request)
        self.logger.info('SEND: <RedirectResponse(%s) >' % ext_url)
        raise web.HTTPTemporaryRedirect(ext_url)

    def client_handler(self, method, ext_url, data):
        self.logger.info('SEND: <ClientRequest %s %s >' % (method, ext_url))
        return aiohttp.request(method, ext_url, data=data)
