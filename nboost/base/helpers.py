"""Utility functions for NBoost classes"""

import time
import tarfile
import functools
from pathlib import Path
from typing import Generator, Callable
from tqdm import tqdm
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk


class TimeContext:
    """Records the time within a func context and stores the latency (in ms)
     within a record (dict)"""
    def __init__(self):
        self.record = dict()

    def __call__(self, func: Callable):
        entry = self.record[func.__name__] = dict(avg=0.0, trips=0)

        @functools.wraps(func)
        def decorator(*args, **kwargs):
            """Decorator for function with a timed contxt"""
            start = time.perf_counter()
            ret = func(*args, **kwargs)
            ms_elapsed = (time.perf_counter() - start) * 1000
            avg = self.mean(entry['avg'], ms_elapsed, entry['trips'] + 1)
            entry['trips'] += 1
            entry['avg'] = avg
            return ret
        return decorator

    @staticmethod
    def mean(previous_avg, new_value, num) -> float:
        """Rolling average"""
        return (previous_avg * num + new_value) / (num + 1)


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


def extract_tar_gz(path: Path, to_dir: Path):
    """Extract tar file from path to specified directory"""
    fileobj = path.open('rb')
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall(path=str(to_dir))
    tar.close()
    fileobj.close()


def es_bulk_index(elastic: Elasticsearch, generator: Generator):
    """Stream documents to Elasticsearch"""
    for okay, response in streaming_bulk(elastic, actions=generator):
        if not okay:
            # failure inserting
            print(response)
