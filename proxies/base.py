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
        self.logger.info('Redirecting request to %s' % self.ext_url)
        raise web.HTTPTemporaryRedirect(self.ext_url + str(request.rel_url))
