from elasticsearch import Elasticsearch
import elasticsearch.helpers
from typing import Generator
from pathlib import Path
from tqdm import tqdm
import requests
import tarfile


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
