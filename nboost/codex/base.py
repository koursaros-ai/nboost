from ..base import StatefulBase
from typing import Tuple
from ..base.types import *


class BaseCodex(StatefulBase):
    SEARCH_METHOD = '*'
    SEARCH_PATH = '/search'
    TRAIN_METHOD = '*'
    TRAIN_PATH = '/train'
    STATUS_METHOD = '*'
    STATUS_PATH = '/status'

    # for testing
    NOT_FOUND_METHOD = '*'
    NOT_FOUND_PATH = '/not_found'
    ERROR_METHOD = '*'
    ERROR_PATH = '/error'

    def __init__(self, multiplier: int = 10, field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.field = field

    def state(self):
        return dict(multiplier=self.multiplier, field=self.field)

    def magnify(self, req: Request) -> Request:
        """ Magnify the size of the request by the multiplier """
        raise NotImplementedError

    def parse(self, req: Request, res: Response) -> Tuple[Query, Choices]:
        """ Parse out the query and choices """
        raise NotImplementedError

    def pack(self,
             req: Request,
             res: Response,
             query: Query,
             choices: Choices,
             ranks: Ranks,
             qid: Qid,
             cids: List[Cid]) -> Response:
        """
        Reformat the proxy response according to the reranked candidates
        mreq is the magnified request.
        """
        raise NotImplementedError

    def pluck(self, req: Request) -> Tuple[Qid, Cid]:
        """ Train path retrieves choice id """
        raise NotImplementedError

    def ack(self, qid: Qid, cid: Cid) -> Response:
        """ acknowledge that train was scheduled """
        raise NotImplementedError

    def catch(self, e: Exception):
        """ format the internal error to send to client """
        raise NotImplementedError

    def pulse(self, state: dict) -> Response:
        raise NotImplementedError
