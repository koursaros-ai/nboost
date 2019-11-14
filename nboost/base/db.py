from .base import StatefulBase
from .types import *
from typing import Tuple, List


class BaseDb(StatefulBase):
    """The db is necessary to store queries and choices for use during training
    and to store tracking statistics."""

    # SEARCH METHOD
    def save(self, query: Query, choices: List[Choice]) -> Tuple[Qid, List[Cid]]:
        """ Save the choices during search for using during train """
        raise NotImplementedError

    # TRAIN METHOD
    def get(self, qid: Qid, cid: List[Cid]) -> Tuple[Query, List[Choice]]:
        """ Return the choice for training """
        raise NotImplementedError

    # TRACK METHOD
    def lap(self, ms: float, cls: str, func: str) -> None:
        """ Do something with the function lap time """
        raise NotImplementedError
