from .base import BaseCodex
from ..base.types import *
from pprint import pformat
import json as JSON


class TestCodex(BaseCodex):

    def topk(self, req):
        return Topk(10)

    def magnify(self, req, topk):
        return req

    def parse(self, req, res):
        return Query(b'test query'), Choices([b'choice 1', b'choice 2'])

    def pack(self, req, res, query, choices, ranks, qid, cids):
        return res

    def pluck(self, req):
        return Qid(1), [Cid(i) for i in range(10)]

    def ack(self, qid, cids):
        return Response({}, b'ack', 200)

    def catch(self, e):
        body = JSON.dumps(dict(error=str(e), type=type(e).__name__))
        return Response({}, body, 500)

    def pulse(self, state):
        return Response({}, pformat(state), 200)
