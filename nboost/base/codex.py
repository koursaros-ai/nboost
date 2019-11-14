from .types import *
from .base import StatefulBase
from typing import Tuple


class BaseCodex(StatefulBase):
    """The role of the ~codex~ is to contain search-api-specific code. For
    instance, the Elasticsearch codex should contain all the code necessary
    to amplify the initial client request, parse and repack the json
    response, and format everything exactly how someone using the search api
    would expect.

    The following route definitions tell the server which paths to handle.
    Any other path/route will be proxied through. Paths/routes are defined as
    {path => route} below.
    """
    SEARCH = (b'/search', [b'GET'])
    TRAIN = (b'/train', [b'POST'])
    STATUS = (b'/status', [b'GET'])

    # for testing
    ERROR = (b'/error', [b'POST'])

    def __init__(self, multiplier: int = 10, field: str = None, **kwargs):
        super().__init__(**kwargs)
        self.multiplier = multiplier
        self.field = field

    def state(self) -> dict:
        return dict(multiplier=self.multiplier, field=self.field)

    # SEARCH METHODS
    def topk(self, req: Request) -> Topk:
        """Figure out how many results the client intended to receive

        :param req: initial (ordinary) client request to the search api
        """

    def magnify(self, req: Request, topk: Topk) -> None:
        """Receive the client request to the api and multiply the size of
        the request by the multiplier.

        :param topk: # results requested by client; see topk()
        :param req: initial client request
        :return Request: request to call to the search api for more results
        """
        raise NotImplementedError

    def parse(self, req: Request, res: Response) -> Tuple[Query, List[Choice]]:
        """Parse the query and choices from the magnified request and response.
        Optionally assign an ident to the query and choices.

        :param req: magnified request
        :param res: magnified response
        """
        raise NotImplementedError

    def pack(self,
             topk: Topk,
             res: Response,
             query: Query,
             choices: List[Choice]) -> None:
        """Reformat the proxy response according to the reranked candidates.

        :param topk: number of results requested; parsed in topk()
        :param res: response to the magnified request
        :param query: original client query.
        :param choices: list of choices List[bytes]
        :param ranks: list of ranks List[int]
        :param qid: query id
        :param cids: list of choice ids
        """
        raise NotImplementedError

    # TRAIN METHODS
    def pluck(self, req: Request) -> Tuple[Qid, List[Cid]]:
        """Pluck the chosen query id and choice id(s) from the train request.
        Choice ids should always be casted to a list for standardization."""
        raise NotImplementedError

    def ack(self, qid: Qid, cids: List[Cid]) -> Response:
        """Acknowledge that train was scheduled for that qid/cid"""
        raise NotImplementedError

    # STATUS METHOD
    def pulse(self, state: dict) -> Response:
        """Format a request for the client that contains the concated state
        for all of the components."""
        raise NotImplementedError

    # ERROR METHOD
    def catch(self, e: Exception) -> Response:
        """All errors caught during any component method will be sent here and
        should be returned to the client/handled."""
        raise NotImplementedError


