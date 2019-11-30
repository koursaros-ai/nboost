"""Utility functions for NBoost classes"""
from typing import Any, Union, List
from json.decoder import JSONDecodeError
from contextlib import suppress
from functools import reduce
from pathlib import Path
import operator
import tarfile
import json
import csv
from tqdm import tqdm
import requests


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


def load_json(json_string: bytes) -> Union[dict, None]:
    """try to load json and return None if decode error"""
    with suppress(JSONDecodeError):
        return json.loads(json_string.decode())


def dump_json(obj: Union[dict, list, str, int, float], **kwargs) -> bytes:
    """Dump dict to json encoded bytes string"""
    return json.dumps(obj, **kwargs).encode()


def count_lines(path: Path):
    """Count the number of lines in a file"""
    return sum(1 for _ in path.open())


def csv_generator(path: Path, columns: List[int], delim: str):
    """yields the designated columns as a generator"""
    with path.open() as file:
        for line in csv.reader(file, delimiter=delim):
            yield [line[idx] for idx in columns]
