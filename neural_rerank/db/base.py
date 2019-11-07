from ..base import StatefulBase
from ..base.types import *
from typing import Tuple


class BaseDb(StatefulBase):
    def save(self, query: Query, choices: List[Choice]) -> None:
        """ Save the choices during search for using during train """
        raise NotImplementedError

    def get(self, pick: Cid) -> Tuple[Query, List[Choice], Labels]:
        """ Return the choice for training """
        raise NotImplementedError
