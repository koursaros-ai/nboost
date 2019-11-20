from .helpers import download_file, extract_tar_gz
from .. import MODEL_MAP, PKG_PATH
from pathlib import Path
from typing import List
from ..base import set_logger


class BaseModel:
    def __init__(self,
                 lr: float = 10e-3,
                 model_dir: str = 'bert-base-uncased-msmarco',
                 data_dir: Path = PKG_PATH.joinpath('.cache'),
                 max_seq_len: int = 128,
                 batch_size: int = 4, **kwargs):
        super().__init__()
        self.lr = lr
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.model_dir = data_dir.joinpath(model_dir).absolute()
        self.logger = set_logger(model_dir)

    def download(self):
        # make sure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.model_dir.exists():
            self.logger.info('Using model cache from %s' % self.model_dir)
        else:
            self.logger.info('Did not find model cache in %s' % self.model_dir)

            if self.model_dir.name in MODEL_MAP:
                url = MODEL_MAP[self.model_dir.name]

                tar_gz_path = self.data_dir.joinpath(Path(url).name)
                if tar_gz_path.exists():
                    self.logger.info('Found model cache in %s' % tar_gz_path)
                else:
                    self.logger.info('Downloading "%s" finetuned model.' % self.model_dir)
                    download_file(url, tar_gz_path)

                self.logger.info('Extracting "%s" from %s' % (self.model_dir, tar_gz_path))
                extract_tar_gz(tar_gz_path, self.data_dir)

                if not self.model_dir.exists():
                    raise NotADirectoryError('Could not download finetuned model '
                                             'to directory "%s".' % self.model_dir)
            else:
                self.logger.warning('Could not find finetuned model "%s" in '
                                    '%s. Falling back to pytorch/tf resolution' % (
                                    self.model_dir, MODEL_MAP.keys()))

    def state(self):
        return dict(lr=self.lr, data_dir=self.data_dir)

    def rank(self, query: str, choices: List[str]) -> List[int]:
        """
        assign relative ranks to each choice
        """
        raise NotImplementedError


