from ..cli import set_logger
from .helpers import pformat


class BaseLogger:
    def __init__(self, verbose=False, **kwargs):
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)
        self.logger.info(pformat({**kwargs, 'verbose': verbose}))



