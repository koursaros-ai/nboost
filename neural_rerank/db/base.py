from ..base import StatefulBase
from ..base.types import *
from typing import Tuple


class BaseDb(StatefulBase):
    def save(self, query: Query, choices: Choices) -> None:
        """ Save the choices during search for using during train """
        raise NotImplementedError

    def get(self, qid: Qid, cid: Cid) -> Tuple[Query, Choices, Labels]:
        """ Return the choice for training """
        raise NotImplementedError

    def lap(self, ms: float, cls: str, func: str) -> None:
        """ Do something with the function lap time """
        raise NotImplementedError
