from .base import StatefulBase
from aiohttp import web
from .types import *
import requests
import tarfile
import sys
import os


class BaseModel(StatefulBase):
    MODEL_PATHS = {
        "bert_base_msmarco": {
            "url": "https://storage.googleapis.com/koursaros/bert_marco.tar.gz",
            "ckpt": "bert_marco/bert_model.ckpt"
        }
    }

    def __init__(self,
                 lr: float = 10e-3,
                 model_ckpt: str ='bert_base_msmarco',
                 data_dir: str = './.cache',
                 max_seq_len: int = 128,
                 batch_size: int = 4, **kwargs):
        super().__init__()
        self.lr = lr
        self.data_dir = data_dir
        self.model_ckpt = model_ckpt
        self.model_dir = os.path.dirname(self.model_ckpt)
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(self.model_dir) and self.model_ckpt in self.MODEL_PATHS:
            model_ckpt_path = os.path.join(self.data_dir, self.MODEL_PATHS[self.model_ckpt]['ckpt'])
            self.model_dir = os.path.dirname(model_ckpt_path)
            if not os.path.exists(self.model_dir):
                file = self.download_model(self.model_ckpt, self.data_dir)
                self.extract_model(file, self.data_dir)
                os.remove(file)
                assert os.path.exists(self.model_dir)
            self.model_ckpt = model_ckpt_path

    def post_start(self):
        """ Executes after the process forks """
        pass

    def state(self):
        return dict(lr=self.lr, data_dir=self.data_dir)

    def train(self, query: Query, choices: Choices, labels: Labels) -> None:
        """ train """
        raise web.HTTPNotImplemented

    def rank(self, query: Query, choices: Choices) -> Ranks:
        """
        sort list of indices of topk candidates
        """
        raise web.HTTPNotImplemented

    def download_model(self, model, data_dir):
        link = self.MODEL_PATHS[model]['url']
        file_name = os.path.join(data_dir, self.MODEL_PATHS[model]['url'].split('/')[-1])
        with open(file_name, "wb") as f:
            print("Downloading %s" % link)
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        return file_name

    @staticmethod
    def extract_model(archive, data_dir):
        print("Extracting %s" % archive)
        tar = tarfile.open(archive)
        tar.extractall(data_dir)
        tar.close()