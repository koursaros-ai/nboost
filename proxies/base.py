from ..base import BaseServer, Response
from .. import models

import itertools
from aiohttp import web, ClientSession


class BaseProxy(BaseServer):
    def __init__(self, model: str = 'BaseModel', ext_host: str = '127.0.0.1',
                 ext_port: int = 53001, **kwargs):
        super().__init__(**kwargs)
        self.ext_url = "http://%s:%s" % (ext_host, ext_port)
        self.model = getattr(models, model)(**kwargs)
        self.counter = itertools.count()
        self.queries = dict()

    async def default_handler(self, request: 'web.BaseRequest'):
        async with ClientSession(headers=request.headers) as session:
            route = (request.method, self.ext_url + str(request.rel_url))
            self.logger.info('Proxying %s request to %s' % route)
            response = await session.request(*route)
            return web.Response(
                body=response.content,
                headers=response.headers,
                status=response.status
            )
