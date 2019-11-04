
import aiohttp
from ..base import Base
from aiohttp import web, client
from typing import Tuple, List


class BaseClient(Base):
    def __init__(self,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 53001,
                 multiplier: int = 10,
                 field: str = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.multiplier = multiplier
        self.field = field

    def client_handler(self, method, ext_url, data):
        self.logger.info('SEND: <ClientRequest %s %s >' % (method, ext_url))
        return aiohttp.request(method, ext_url, data=data)

    def ext_url(self, request: web.BaseRequest):
        return request.url.with_host(self.ext_host).with_port(self.ext_port)

    async def not_found_handler(self, request: web.BaseRequest):
        ext_url = self.ext_url(request)
        self.logger.info('SEND: <RedirectResponse(%s) >' % ext_url)
        raise web.HTTPTemporaryRedirect(ext_url)

    def status(self):
        return dict(ext_host=self.ext_host, ext_port=self.ext_port)

    async def magnify(self, request: web.BaseRequest) -> Tuple[int, str, str, bytes]:
        """
        Magnify the size of the request by the multiplier
        :return topk, method, ext_url, data
        """
        raise web.HTTPNotImplemented

    async def parse(self,
                    request: web.BaseRequest,
                    client_response: client.ClientResponse) -> Tuple[str, List[str]]:
        """
        Parse out the query and candidates
        :return: query, candidates
        """
        raise web.HTTPNotImplemented

    async def format(self, client_response: client.ClientResponse, reranked: List[str]) -> web.Response:
        """
        Reformat the client response according to the reranked candidates
        """
        raise web.HTTPNotImplemented