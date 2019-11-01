from . import BaseServer, Response
from .. import models
import itertools
from aiohttp import web


class BaseProxy(BaseServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queries = dict()
        self.model = getattr(models, self.args.model)(self.args)
        self.counter = itertools.count()

    async def default_handler(self, request: 'web.BaseRequest'):
        return Response.status_404()