import json
from aiohttp import web


async def parse_json_request_qid_cid(request: web.BaseRequest):
    req = await request.read()
    try:
        b = json.loads(req)
    except json.decoder.JSONDecodeError:
        b = {}

    q = request.query
    h = request.headers
    qid = b['qid'] if 'qid' in b else q['qid'] if 'qid' in q else h['qid'] if 'qid' in h else None
    cid = b['qid'] if 'qid' in b else q['qid'] if 'qid' in q else h['qid'] if 'qid' in h else None

    if qid:
        qid = int(qid)
    else:
        raise ValueError('Could not find qid in body, query, or headers')

    if cid:
        cid = int(cid)
    else:
        raise ValueError('Could not find cid in body, query, or headers')

    return qid, cid