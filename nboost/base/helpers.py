from elasticsearch import Elasticsearch
import elasticsearch.helpers
from typing import Generator, Callable
from pathlib import Path
from tqdm import tqdm
import requests
import tarfile
import time


class TimeContext:
    """Records the time within a with() context and stores the latency (in ms)
     within a record (dict)"""
    def __init__(self):
        self.record = dict()

    def __call__(self, f: Callable):
        entry = self.record[f.__name__] = dict(avg=0, trips=0)

        def decorator(*args, **kwargs):
            start = time.perf_counter()
            ret = f(*args, **kwargs)
            ms_elapsed = (time.perf_counter() - start) * 1000
            avg = self.mean(entry['avg'], ms_elapsed, entry['trips'] + 1)
            entry['trips'] += 1
            entry['avg'] = avg
            return ret
        return decorator

    @staticmethod
    def mean(previous_avg, new_value, n) -> float:
        return (previous_avg * n + new_value) / (n + 1)


def download_file(url: str, path: Path):
    fileobj = path.open('wb+')
    response = requests.get(url=url, stream=True)
    content_length = response.headers.get('content-length')

    if content_length is None:  # no content length header
        raise ConnectionAbortedError('No content-length header on request.')
    else:
        pbar = tqdm(total=int(content_length), unit='B', desc=url)
        for data in response.iter_content(chunk_size=4096):
            fileobj.write(data)
            pbar.update(4096)
        pbar.close()
    fileobj.close()


def extract_tar_gz(path: Path, to_dir: Path):
    fileobj = path.open('rb')
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall(path=str(to_dir))
    tar.close()
    fileobj.close()


def es_bulk_index(es: Elasticsearch, g: Generator):
    for ok, response in elasticsearch.helpers.streaming_bulk(es, actions=g):
        if not ok:
            # failure inserting
            print(response)
