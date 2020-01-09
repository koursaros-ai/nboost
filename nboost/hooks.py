"""Called at specific times during the proxy loop."""
from nboost.helpers import prepare_response, prepare_request, dump_json
from nboost.protocol import HttpProtocol
from nboost.models.base import BaseModel
from nboost.models.qa import QAModel
from nboost.session import Session
from nboost.exceptions import *
from pathlib import Path
import socket
import time
import re


def on_frontend_request(client_socket: socket.socket, session: Session):
    """Send a the static frontend to the client."""
    response = {}
    protocol = HttpProtocol()
    frontend_path = Path(__file__).parent.parent.joinpath('resources/frontend')
    protocol.set_response_parser()
    protocol.set_response(response)
    url_path = session.request['url']['path']

    if url_path == '/nboost':
        asset = 'index.html'
    else:
        asset = url_path.replace('/nboost/', '', 1)

    asset_path = frontend_path.joinpath(asset)

    # for security reasons, make sure there is no access to other dirs
    if frontend_path in asset_path.parents and asset_path.exists():
        response['body'] = asset_path.read_bytes()
    else:
        response['body'] = frontend_path.joinpath('404.html').read_bytes()

    client_socket.send(prepare_response(response))


def on_status_request(client_socket, status: dict):
    """Send a the static frontend to the client."""
    response = {}
    protocol = HttpProtocol()
    protocol.set_response_parser()
    protocol.set_response(response)
    response['body'] = status
    response['body'] = dump_json(response['body'], indent=2)
    client_socket.send(prepare_response(response))


def on_unhandled_request(client_socket, server_socket, session: Session):
    """Send buffered request to server and receive the rest of the original
    client request"""
    protocol = HttpProtocol()
    protocol.set_request_parser()
    protocol.add_data_hook(server_socket.send)
    protocol.feed(session.buffer)
    protocol.recv(client_socket)
    protocol = HttpProtocol()
    protocol.set_response_parser()
    protocol.add_data_hook(client_socket.send)
    protocol.recv(server_socket)


def on_client_request(client_socket, session: Session, search_path: str):
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


def on_server_request(server_socket: socket.socket, session: Session):
    """Send magnified request to the server"""
    body = dump_json(session.request['body'])
    session.request['headers']['content-type'] = 'application/json; charset=UTF-8'
    request = {**session.request, 'body': body}
    server_socket.send(prepare_request(request))


def on_server_response(server_socket: socket.socket, session: Session):
    """Receive magnified request from the server"""
    protocol = HttpProtocol()
    protocol.set_response_parser()
    protocol.set_response(session.response)
    protocol.recv(server_socket)

    if session.response['status'] >= 400:
        raise UpstreamServerError


def on_client_response(session: Session, client_socket):
    """Send the ranked results to the client"""
    kwargs = dict(indent=2) if 'pretty' in session.request['url']['query'] else {}
    session.response['body'] = dump_json(session.response['body'], **kwargs)
    client_socket.send(prepare_response(session.response))


def on_proxy_error(client_socket, exc: Exception):
    """Send internal server error to the client."""
    response = {}
    protocol = HttpProtocol()
    protocol.set_response(response)
    response['body'] = dump_json({'error': repr(exc)}, indent=2)
    response['status'] = 500
    client_socket.send(prepare_response(response))


def on_rerank(model: BaseModel, session: Session) -> float:
    """Returns the time the model takes to rerank."""
    start_time = time.perf_counter()
    ranks = model.rank(session.query, session.cvalues)[:session.topk]
    total_time = time.perf_counter() - start_time
    reranked_choices = [session.choices[rank] for rank in ranks]
    session.set_response_path(session.choices_path, reranked_choices)
    return total_time


def on_qa(qa_model: QAModel, session: Session, qa_threshold: float) -> float:
    """Returns the qa time."""
    start_time = time.perf_counter()
    answer, start_pos, stop_pos, score = qa_model.get_answer(session.query, session.cvalues[0])
    total_time = time.perf_counter() - start_time

    if score > qa_threshold:
        session.response['body']['nboost']['answerStartPos'] = start_pos
        session.response['body']['nboost']['answerStopPos'] = stop_pos

    return total_time

