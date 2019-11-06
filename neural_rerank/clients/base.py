
from ..base import BaseLogger, BaseHandler
from aiohttp import web, client
from typing import Tuple, List


class BaseClient(BaseLogger):
    handler = BaseHandler()
    status_method = '*'
    search_method = '*'
    train_method = '*'
    status_path = '/status'
    search_path = '/search'
    train_path = '/train'

    def __init__(self,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 53001,
                 multiplier: int = 10,
                 field: str = None,
                 **kwargs):
        super().__init__()
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.multiplier = multiplier
        self.field = field

    @handler.add_state
    def ext_host(self):
        return self.ext_host

    @handler.add_state
    def ext_port(self):
        return self.ext_port

    @handler.add_state
    def multiplier(self):
        return self.multiplier

    @handler.add_state
    def field(self):
        return self.field

    def ext_url(self, request: web.BaseRequest):
        return request.url.with_host(self.ext_host).with_port(self.ext_port)

    async def not_found_handler(self, request: web.BaseRequest):
        ext_url = self.ext_url(request)
        self.logger.info('SEND: <RedirectResponse(%s) >' % ext_url)
        raise web.HTTPTemporaryRedirect(ext_url)

    def status(self):
        return dict(ext_host=self.ext_host, ext_port=self.ext_port)

    async def magnify_request(self, request: web.BaseRequest) -> Tuple[int, str, str, bytes]:
        """
        Magnify the size of the request by the multiplier
        :return topk, method, ext_url, data
        """
        raise web.HTTPNotImplemented

    async def parse_query_candidates(self,
                                     request: web.BaseRequest,
                                     client_response: client.ClientResponse) -> Tuple[str, List[str]]:
        """
        Parse out the query and candidates
        :return: query, candidates
        """
        raise web.HTTPNotImplemented

    async def format_response(self,
                              client_response: client.ClientResponse,
                              topk: int,
                              ranks: List[int],
                              qid: int) -> web.Response:
        """
        Reformat the client response according to the reranked candidates
        """
        raise web.HTTPNotImplemented

    async def parse_qid_cid(self, request: web.BaseRequest) -> Tuple[int, int]:
        """
        Parse out the qid and cid
        :return: qid, cid
        """
        raise web.HTTPNotImplemented
