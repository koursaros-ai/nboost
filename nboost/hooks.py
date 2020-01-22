"""Called at specific times during the proxy loop."""

from pathlib import Path
from copy import deepcopy
import requests
import socket
import time
import re
from requests import ConnectionError
from nboost.protocol import HttpProtocol
from nboost.models.rerank.base import RerankModel
from nboost.models.qa.base import QAModel
from nboost.session import Session
from nboost.exceptions import *
from nboost import defaults
from nboost.helpers import (
    prepare_response,
    dump_json,
    unparse_url,
    calculate_mrr,
    calculate_overlap)


def connect_to_server(server_socket, uhost, uport):
    """Connect the socket to the server."""
    try:
        server_socket.connect((uhost, uport))
    except ConnectionRefusedError:
        raise UpstreamConnectionError(uhost, uport)


def on_frontend_request(client_socket: socket.socket, session: Session):
    """Send a the static frontend to the client."""
    protocol = HttpProtocol()
    frontend_path = Path(__file__).parent.joinpath('resources/frontend')
    protocol.set_response(session.response)
    url_path = session.request['url']['path']

    if url_path == '/nboost':
        asset = 'index.html'
    else:
        asset = url_path.replace('/nboost/', '', 1)

    asset_path = frontend_path.joinpath(asset)

    # for security reasons, make sure there is no access to other dirs
    if frontend_path in asset_path.parents and asset_path.exists():
        session.response['body'] = asset_path.read_bytes()
    else:
        session.response['body'] = frontend_path.joinpath('404.html').read_bytes()

    prepared_response = prepare_response(session.response)
    client_socket.send(prepared_response)


def on_status_request(client_socket, session: Session, status: dict):
    """Send a the static frontend to the client."""
    protocol = HttpProtocol()
    protocol.set_response(session.response)
    session.response['body'] = status
    session.response['body'] = dump_json(session.response['body'], indent=2)
    prepared_response = prepare_response(session.response)
    client_socket.send(prepared_response)


def on_unhandled_request(client_socket, server_socket, session: Session):
    """Send buffered request to server and receive the rest of the original
    client request"""
    protocol = HttpProtocol()
    protocol.set_request_parser()
    try:
        connect_to_server(server_socket, session.uhost, session.uport)
    except UpstreamConnectionError as exc:
        on_proxy_error(client_socket, exc)
    else:
        protocol.add_data_hook(server_socket.send)
        protocol.feed(session.buffer)
        protocol.recv(client_socket)
        protocol = HttpProtocol()
        protocol.set_response_parser()
        protocol.add_data_hook(client_socket.send)
        protocol.recv(server_socket)


def on_client_request(session: Session, client_socket, search_path: str):
    """Receive client request and pipe to buffer in case of exceptions"""

    def on_url(url: dict):
        if url['path'].startswith('/nboost/status'):
            raise StatusRequest

        if url['path'].startswith('/nboost'):
            raise FrontendRequest

        if not re.match(search_path, url['path']):
            raise UnknownRequest

    protocol = HttpProtocol()
    protocol.set_request_parser()
    protocol.set_request(session.request)
    protocol.add_data_hook(session.buffer.extend)
    protocol.add_url_hook(on_url)
    protocol.recv(client_socket)


def on_server_request(session: Session):
    """Send magnified response to the server"""
    request = deepcopy(session.request)
    request['headers'].pop('host', '')
    request['body'].pop('nboost', '')

    for config in session.cli_configs:
        request['url']['query'].pop(config, '')

    try:
        response = requests.request(
            method=request['method'],
            url='{protocol}://{host}:{port}{path}'.format(
                protocol='https' if session.ussl else 'http',
                host=session.uhost,
                port=session.uport,
                path=unparse_url(request['url'])
            ),
            headers=request['headers'],
            json=request['body']
        )

    except ConnectionError as exc:
        raise UpstreamServerError(exc)

    session.response['status'] = response.status_code
    session.response['headers'] = {k.lower(): v for k, v in response.headers.items()}
    session.response['body'].update(response.json())
    session.response['version'] = 'HTTP/1.1'
    session.response['reason'] = response.reason

    if response.status_code >= 400:
        raise UpstreamServerError(response.text)

    session.stats['choices'] = len(session.choices)


def on_client_response(session: Session, client_socket):
    """Send the ranked results to the client"""
    kwargs = dict(indent=2) if 'pretty' in session.request['url']['query'] else {}
    session.response['body'] = dump_json(session.response['body'], **kwargs)
    prepared_response = prepare_response(session.response)
    client_socket.send(prepared_response)


def on_proxy_error(client_socket, exc: Exception):
    """Send internal server error to the client."""
    session = Session()
    protocol = HttpProtocol()
    protocol.set_response(session.response)
    session.response['body'] = dump_json({'error': repr(exc)}, indent=2)
    session.response['status'] = 500
    prepared_response = prepare_response(session.response)
    client_socket.send(prepared_response)


def on_rerank_request(session: Session):
    """Magnify the size of the request to topn results."""
    session.stats['topk'] = session.topk
    session.set_request_path(session.topk_path, session.topn)


def on_rerank_response(session: Session, model: RerankModel):
    if session.rerank_cids:
        session.stats['server_mrr'] = calculate_mrr(session.rerank_cids, session.cids)

    start_time = time.perf_counter()

    ranks = model.rank(
        query=session.query,
        choices=session.cvalues,
        filter_results=session.filter_results
    )

    session.stats['rerank_time'] = time.perf_counter() - start_time
    reranked_choices = [session.choices[rank] for rank in ranks]
    session.set_response_path(session.choices_path, reranked_choices)

    if session.rerank_cids:
        session.stats['model_mrr'] = calculate_mrr(session.rerank_cids, session.cids)

    # this is hacky and needs to be fixed
    topk = session.stats['topk']

    session.set_response_path(session.choices_path, session.choices[:topk])


def on_qa(session: Session, qa_model: QAModel):
    """Returns the qa time."""

    if session.cvalues:
        start_time = time.perf_counter()
        answer, start_pos, stop_pos, score = qa_model.get_answer(session.query, session.cvalues[0])
        session.stats['qa_time'] = time.perf_counter() - start_time

        if score > session.qa_threshold:
            session.add_nboost_response('answer_text', answer)
            session.add_nboost_response('answer_start_pos', start_pos)
            session.add_nboost_response('answer_stop_pos', stop_pos)

        if session.cids:
            first_choice_id = session.cids[0]
            if first_choice_id in session.qa_cids:
                qa_start_pos, qa_end_pos = session.qa_cids[first_choice_id]
                session.stats['qa_overlap'] = calculate_overlap(qa_start_pos,
                                                                qa_end_pos,
                                                                qa_start_pos,
                                                                qa_end_pos)


def on_debug(session: Session):
    """Add session configs to nboost response for debugging."""
    for config in session.cli_configs:
        session.add_nboost_response(config, getattr(session, config))

    session.add_nboost_response('query', session.query)
    session.add_nboost_response('topk', session.stats['topk'])
    session.add_nboost_response('cvalues', session.cvalues)

