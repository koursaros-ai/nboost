"""Utility functions for NBoost classes"""
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
from json.decoder import JSONDecodeError
from typing import Any, Union, List
from http.client import responses
from contextlib import suppress
from functools import reduce
from pathlib import Path
import importlib
import operator
import tarfile
import json
from jsonpath_ng.ext import parse
from jsonpath_ng import jsonpath
from tqdm import tqdm
import requests

JSONTYPES = Union[dict, list, str, int, float]


def update(self, data, val):
    """JsonPath Union class patch to support updating."""
    with suppress(TypeError):
        self.left.update(data, val)

    with suppress(TypeError):
        self.right.update(data, val)


jsonpath.Union.update = update


def parse_url(url: bytes) -> dict:
    """Parses a url bytes string in the form of:
        scheme://netloc/path;params?query#fragment

    Returns a dictionary with the respective keys value pairs."""
    url = urlparse(url.decode())
    qsl = parse_qsl(url.query, keep_blank_values=True)
    return {
        'scheme': url.scheme,
        'netloc': url.netloc,
        'path': url.path,
        'params': url.params,
        'fragment': url.fragment,
        'query': dict(qsl) if url.query else {}
    }


def unparse_url(url: dict) -> str:
    """Reformats a url produced in parse_url()"""
    return urlunparse((
        url['scheme'],
        url['netloc'],
        url['path'],
        url['params'],
        urlencode(url['query']),
        url['fragment']
    ))


def prepare_request(request: dict) -> bytes:
    """Prepares a request with the following keys:
        version: str
        headers: dict
        url: dict
        body: bytes
        method: str"""

    # cast request sections to strings
    request['headers'].pop('content-encoding', '')
    request['headers']['content-length'] = len(request['body'])
    request = {
        'body': request['body'],
        'url': unparse_url(request['url']),
        'headers': ''.join('\r\n%s: %s' % (k, v) for k, v in request['headers'].items()),
        'method': request['method'],
        'version': request['version']
    }

    return '{method} {url} {version}{headers}\r\n\r\n'.format(**request).encode() + request['body']


def prepare_response(response: dict) -> bytes:
    """Prepares a request with the following keys:
        version: str
        status: int
        headers: dict
        body: bytes"""
    response['reason'] = responses[response['status']]
    response['headers'].pop('content-encoding', '')
    response['headers']['content-length'] = str(len(response['body']))
    response['headers'] = ''.join('\r\n%s: %s' % (k, v) for k, v in response['headers'].items())

    return '{version} {status} {reason}{headers}\r\n\r\n'.format(**response).encode() + response['body']


def get_jsonpath(obj: JSONTYPES, path: str) -> List[JSONTYPES]:
    """Return json values matching jsonpaths."""
    return [match.value for match in parse(path).find(obj)]


def set_jsonpath(obj: JSONTYPES, path: str, value: Any) -> None:
    """Sets the value in each matching jsonpath key."""
    expression = parse(path)
    expression.update(obj, value)


def download_file(url: str, path: Path):
    """Download file from a specified url to a given path"""
    fileobj = path.open('wb+')
    response = requests.get(url=url, stream=True)
    content_length = response.headers.get('content-length')

    if content_length is None:  # no content length header
        raise ConnectionAbortedError('No content-length header on request.')
    pbar = tqdm(total=int(content_length), unit='B', desc=url)
    for data in response.iter_content(chunk_size=4096):
        fileobj.write(data)
        pbar.update(4096)
    pbar.close()
    fileobj.close()


def extract_tar_gz(path: Path, to_dir: Path = None):
    """Extract tar file from path to specified directory"""
    if to_dir is None:
        to_dir = path.parent

    fileobj = path.open('rb')
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall(path=str(to_dir))
    tar.close()
    fileobj.close()


def get_by_path(root: dict, items: list) -> Any:
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root: dict, items: list, value: Any):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


def load_json(json_string: bytes) -> dict:
    """try to load json and return empty dict if decode error"""
    with suppress(JSONDecodeError):
        return json.loads(json_string.decode())
    return {}


def dump_json(obj: JSONTYPES, **kwargs) -> bytes:
    """Dump dict to json encoded bytes string"""
    return json.dumps(obj, **kwargs).encode()


def count_lines(path: Path):
    """Count the number of lines in a file"""
    fileobj = path.open()
    count = sum(1 for _ in fileobj)
    fileobj.close()
    return count


def flatten(array: list):
    """Flatten nested list to a single list"""
    return [item for sublist in array for item in sublist]


def import_class(module: str, cls: str):
    """import an nboost class from a module."""
    file = 'nboost.%s' % module
    return getattr(importlib.import_module(file), cls)
