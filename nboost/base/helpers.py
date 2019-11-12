from typing import Union, BinaryIO
from pathlib import Path
import requests
import tarfile
from tqdm import tqdm


def download_file(url: str, fileobj: BinaryIO):
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


def extract_tar_gz(fileobj: BinaryIO, data_dir: Union[str, Path]):
    tar = tarfile.open(fileobj=fileobj)
    tar.extractall(path=str(data_dir))
    tar.close()
