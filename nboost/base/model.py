from .helpers import download_file, extract_tar_gz
from .. import MODEL_MAP, PKG_PATH
from .base import StatefulBase
from .types import *
from pathlib import Path


class BaseModel(StatefulBase):
    def __init__(self,
                 lr: float = 10e-3,
                 model_dir: str = 'bert_marco',
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

        # make sure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.model_dir.exists():
            self.logger.info('Using model cache from %s' % self.model_dir)
        else:
            self.logger.info('Did not find model cache in %s' % self.model_dir)

            if model_dir in MODEL_MAP:
                url = MODEL_MAP[model_dir]

                tar_gz_path = self.data_dir.joinpath(Path(url).name)
                if tar_gz_path.exists():
                    self.logger.info('Found model cache in %s' % tar_gz_path)
                else:
                    w = tar_gz_path.open('wb+')
                    self.logger.info('Downloading "%s" finetuned model.' % model_dir)
                    download_file(url, w)
                    w.close()

                r = tar_gz_path.open('rb')
                self.logger.info('Extracting "%s" from %s' % (model_dir, tar_gz_path))
                extract_tar_gz(r, self.data_dir)
                r.close()

                if not self.model_dir.exists():
                    raise NotADirectoryError('Could not download finetuned model '
                                             'to directory "%s".' % self.model_dir)
            else:
                self.logger.warning('Could not find finetuned model "%s" in '
                                    '%s. Falling back to pytorch/tf resolution' % (
                                    model_dir, MODEL_MAP.keys()))

    def post_start(self):
        """ Executes after the process forks """
        pass

    def state(self):
        return dict(lr=self.lr, data_dir=self.data_dir)

    def train(self, query: Query, choices: Choices, labels: Labels) -> None:
        """ train """
        raise NotImplementedError

    def rank(self, query: Query, choices: Choices) -> Ranks:
        """
        sort list of indices of topk candidates
        """
        raise NotImplementedError


