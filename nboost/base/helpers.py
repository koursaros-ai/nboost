from typing import BinaryIO
from pathlib import Path
import requests
import tarfile
from tqdm import tqdm


def download_file(url: str, path: Path):
    fileobj: BinaryIO = path.open('wb+')
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
    fileobj: BinaryIO = path.open('rb')
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall(path=str(to_dir))
    tar.close()
    fileobj.close()
