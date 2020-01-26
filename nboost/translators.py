from urllib.parse import ParseResult, urlparse, parse_qsl, urlencode
import json
from requests import Response as RequestsResponse, request as requests_request
from flask import Response as FlaskResponse
from werkzeug.local import LocalProxy

__all__ = [
    'flask_request_to_dict_request',
    'dict_request_to_requests_response',
    'requests_response_to_dict_response',
    'dict_response_to_flask_response',
    'requests_response_to_flask_response'
]


def flask_request_to_dict_request(flask_request: LocalProxy) -> dict:
    """Convert flask request to dict request."""
    urllib_url = urlparse(flask_request.url)

    return {
        'headers': dict(flask_request.headers),
        'method': flask_request.method,
        'url': {
            'scheme': urllib_url.scheme,
            'netloc': urllib_url.netloc,
            'path': urllib_url.path,
            'params': urllib_url.params,
            'query': dict(parse_qsl(urllib_url.query)),
            'fragment': urllib_url.fragment
        },
        'body': dict(flask_request.json) if flask_request.json else {}
    }


def flask_request_to_requests_response(flask_request: LocalProxy) -> RequestsResponse:
    urllib_url = urlparse(flask_request.url)

    return requests_request(
        headers=flask_request.headers,
        method=flask_request.method,
        url=ParseResult(
            scheme=urllib_url.scheme
        )
    )


def dict_request_to_requests_response(dict_request: dict) -> RequestsResponse:
    return requests_request(
        headers=dict_request['headers'],
        method=dict_request['method'],
        url=ParseResult(
            scheme=dict_request['url']['scheme'],
            netloc=dict_request['url']['netloc'],
            path=dict_request['url']['path'],
            params=dict_request['url']['params'],
            query=urlencode(dict_request['url']['query'], quote_via=lambda x, *a: x),
            fragment=dict_request['url']['fragment']
        ).geturl(),
        json=dict_request['body']
    )


def requests_response_to_dict_response(requests_response: RequestsResponse) -> dict:
    requests_response.headers.pop('content-encoding', '')
    requests_response.headers.pop('content-length', '')
    requests_response.headers.pop('transfer-encoding', '')
    return {
        'status': requests_response.status_code,
        'headers': dict(requests_response.headers),
        'body': requests_response.json()
    }


def requests_response_to_flask_response(requests_response: RequestsResponse) -> FlaskResponse:
    requests_response.headers.pop('content-encoding', '')
    requests_response.headers.pop('transfer-encoding', '')
    requests_response.headers.pop('content-length', '')
    return FlaskResponse(
        response=requests_response.content,
        status=requests_response.status_code,
        headers=dict(requests_response.headers)
    )


def dict_response_to_flask_response(dict_response: dict) -> FlaskResponse:
    return FlaskResponse(
        response=json.dumps(dict_response['body']),
        status=dict_response['status'],
        headers=dict_response['headers'],
    )