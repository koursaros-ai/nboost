import json
from aiohttp import web


async def parse_json_request_qid_cid(request: web.BaseRequest):
    try:
        b = await request.json()
    except json.decoder.JSONDecodeError:
        b = {}

    q = request.query
    h = request.headers
    qid = b['qid'] if 'qid' in b else q['qid'] if 'qid' in q else h['qid'] if 'qid' in h else None
    cid = b['cid'] if 'cid' in b else q['cid'] if 'cid' in q else h['cid'] if 'cid' in h else None

    if qid:
        qid = int(qid)
    else:
        raise ValueError('Could not find qid in body, query, or headers')

    if cid:
        cid = int(cid)
    else:
        raise ValueError('Could not find cid in body, query, or headers')

    return qid, cid