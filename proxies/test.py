from .base import BaseProxy, Response
from typing import Tuple, List
from aiohttp import web


class TestProxy(BaseProxy):
    routes = web.RouteTableDef()

    @routes.get('/test')
    async def test(self, request):
        return Response.json_200(dict(msg='Success'))
