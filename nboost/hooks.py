"""Called at specific times during the proxy loop."""
from nboost.helpers import prepare_response, prepare_request, dump_json
from nboost.protocol import HttpProtocol
from nboost.models.qa import QAModel
from nboost.exceptions import *
from pathlib import Path
import socket
import re


def on_frontend_request(client_socket, request):
    """Send a the static frontend to the client."""
    response = {}
    protocol = HttpProtocol()
    frontend_path = Path(__file__).parent.parent.joinpath('resources/frontend')
    protocol.set_response_parser()
    protocol.set_response(response)
    url_path = request['url']['path']

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


def on_unhandled_request(client_socket, server_socket, buffer: bytearray):
    """Send buffered request to server and receive the rest of the original
    client request"""
    protocol = HttpProtocol()
    protocol.set_request_parser()
    protocol.add_data_hook(server_socket.send)
    protocol.feed(buffer)
    protocol.recv(client_socket)
    protocol = HttpProtocol()
    protocol.set_response_parser()
    protocol.add_data_hook(client_socket.send)
    protocol.recv(server_socket)


def on_client_request(client_socket, request: dict, buffer: bytearray,
                      search_path: str):
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
    protocol.set_request(request)
    protocol.add_data_hook(buffer.extend)
    protocol.add_url_hook(on_url)
    protocol.recv(client_socket)


def on_server_request(server_socket: socket.socket, request: dict):
    """Send magnified request to the server"""
    request['body'] = dump_json(request['body'])
    request['headers']['content-type'] = 'application/json; charset=UTF-8'
    server_socket.send(prepare_request(request))


def on_server_response(server_socket: socket.socket, response: dict):
    """Receive magnified request from the server"""
    protocol = HttpProtocol()
    protocol.set_response_parser()
    protocol.set_response(response)
    protocol.recv(server_socket)

    if response['status'] >= 400:
        raise UpstreamServerError


def on_client_response(request: dict, response: dict, client_socket):
    """Send the ranked results to the client"""
    kwargs = dict(indent=2) if 'pretty' in request['url']['query'] else {}
    response['body'] = dump_json(response['body'], **kwargs)
    client_socket.send(prepare_response(response))


def on_proxy_error(client_socket, exc: Exception):
    """Send internal server error to the client."""
    response = {}
    protocol = HttpProtocol()
    protocol.set_response(response)
    response['body'] = dump_json({'error': repr(exc)}, indent=2)
    response['status'] = 500
    client_socket.send(prepare_response(response))


def on_qa_model_request(qa_model: QAModel, response: dict, query: str, cvalue: str):
    answer, offsets, score = qa_model.get_answer(query, cvalue)
    response['body']['nboost']['qa_model'] = answer
    response['body']['nboost']['qa_model_offsets'] = offsets
    response['body']['nboost']['qa_model_score'] = score
