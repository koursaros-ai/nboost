"""Base Class for ranking models"""

from nboost.logger import set_logger
from nboost.plugins import Plugin
from nboost import defaults


class ModelPlugin(Plugin):
    """Base Class for Transformer Models"""
    def __init__(self, model_dir: type(defaults.model_dir) = defaults.model_dir,
                 batch_size: type(defaults.batch_size) = defaults.batch_size,
                 max_seq_len: type(defaults.max_seq_len) = defaults.max_seq_len,
                 verbose: type(defaults.verbose) = defaults.verbose,
                 lr: type(defaults.lr) = defaults.lr, **_):
        """Model dir will be a full path if the binary is present, and will
        be just the name of the "model_dir" if it is not."""
        super().__init__()
        self.model_dir = model_dir
        self.lr = lr
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size
        self.logger = set_logger(model_dir, verbose=verbose)

    def close(self):
        """Close model method."""
