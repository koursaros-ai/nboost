from ..base import *
from pprint import pformat
import json as JSON


class TestCodex(BaseCodex):

    def topk(self, req):
        return Topk(10)

    def magnify(self, req, topk):
        return req

    def parse(self, req, res):
        return Query(b'test query'), [Choice(b'choice 1'), Choice(b'choice 2')]

    def pack(self, req, res, query, choices):
        return res

    def pluck(self, req):
        return Qid(1), [Cid(i) for i in range(10)]

    def ack(self, qid, cids):
        return Response(b'HTTP/1.1', 200, {}, b'ack')

    def catch(self, e):
        body = JSON.dumps(dict(error=str(e), type=type(e).__name__)).encode()
        return Response(b'HTTP/1.1', 500, {}, body)

    def pulse(self, state):
        return Response(b'HTTP/1.1', 200, {}, pformat(state))

