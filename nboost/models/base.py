"""Base Class for ranking models"""

from pathlib import Path
from typing import List
import os
from nboost.helpers import download_file, extract_tar_gz
from nboost.logger import set_logger
from nboost.maps import MODEL_MAP
from nboost import PKG_PATH


class BaseModel:
    """Base Class for Transformer Models"""
    MODEL_DIR = str()

    def __init__(self, lr: float = 10e-3, model_dir: str = str(),
                 data_dir: Path = PKG_PATH.joinpath('.cache'),
                 max_seq_len: int = 128, batch_size: int = 4, **_):
        super().__init__()
        self.data_dir = data_dir
        model_dir = model_dir if model_dir else self.MODEL_DIR
        self.model_dir = self.resolve_model_dir(model_dir)
        self.lr = lr
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size
        self.logger = set_logger(model_dir)

    def resolve_model_dir(self, directory: str):
        if not os.path.exists(directory):
            model_dir = self.data_dir.joinpath(directory).absolute()
        else:
            self.logger.info('Using custom model at path %s' % directory)
            model_dir = Path(directory)
        return model_dir

    def download(self):
        """Download the model binary and cache to the package path"""
        # make sure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.model_dir.exists():
            self.logger.info('Using model cache from %s', self.model_dir)
        else:
            self.logger.info('Did not find model cache in %s', self.model_dir)

            if self.model_dir.name in MODEL_MAP:
                url = MODEL_MAP[self.model_dir.name]

                tar_gz_path = self.data_dir.joinpath(Path(url).name)
                if tar_gz_path.exists():
                    self.logger.info('Found model cache in %s', tar_gz_path)
                else:
                    self.logger.info('Downloading "%s" model.', self.model_dir)
                    download_file(url, tar_gz_path)

                self.logger.info('Extracting "%s" from %s', self.model_dir,
                                 tar_gz_path)
                extract_tar_gz(tar_gz_path, self.data_dir)

                if not self.model_dir.exists():
                    raise NotADirectoryError('Could not download finetuned '
                                             'model to "%s".' % self.model_dir)
            else:
                self.logger.warning('Could not find finetuned model "%s" in '
                                    '%s. Falling back to pytorch/tf',
                                    self.model_dir, MODEL_MAP.keys())

    def rank(self, query: str, choices: List[str]) -> List[int]:
        """assign relative ranks to each choice"""

    def close(self):
        """Close the model"""
