"""Base Class for ranking models"""

from typing import List
from nboost.logger import set_logger


class BaseModel:
    """Base Class for Transformer Models"""
    def __init__(self, model_dir: str, lr: float = 10e-3, batch_size: int = 4,
                 max_seq_len: int = 128, verbose: bool = False, filter_results: bool = False,  **_):
        """Model dir will be a full path if the binary is present, and will
        be just the name of the "model_dir" if it is not."""
        super().__init__()
        self.filter_results = filter_results
        self.model_dir = model_dir
        self.lr = lr
        self.max_seq_len = max_seq_len
        self.batch_size = batch_size
        self.logger = set_logger(model_dir, verbose=verbose)

    def rank(self, query: str, choices: List[str]) -> List[int]:
        """assign relative ranks to each choice"""

    def close(self):
        """Close the model"""
