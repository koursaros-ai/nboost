from ..base import BaseServer, Response, RouteHandler
from .. import models
from typing import Tuple
import itertools
from aiohttp import web, client
import aiohttp


class BaseProxy(BaseServer):
    handler = RouteHandler()

    def __init__(self, model: str = 'BaseModel', ext_host: str = '127.0.0.1',
                 ext_port: int = 53001, **kwargs):
        super().__init__(**kwargs)
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.model = getattr(models, model)(**kwargs)
        self.counter = itertools.count()
        self.queries = dict()

    def ext_url(self, request: 'web.BaseRequest'):
        return (
            request
            .url
            .with_host(self.ext_host)
            .with_port(self.ext_port)
            .human_repr()
        )

    async def default_handler(self, request: 'web.BaseRequest'):
        ext_url = self.ext_url(request)
        self.logger.info('Redirecting request to %s' % ext_url)

        raise web.HTTPTemporaryRedirect(ext_url)

    def client_handler(self, method, ext_url, data):
        self.logger.info('<Request %s %s>' % (method, ext_url))
        return aiohttp.request(method, ext_url, data=data)
