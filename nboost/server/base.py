
from typing import Dict, Tuple, Callable
from threading import Thread, Event
from ..base import StatefulBase
from ..base.types import *


def running_avg(avg: float, new: float, n: int):
    return (avg * n + new) / n


class BaseServer(StatefulBase, Thread):

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 54001,
                 **kwargs):
        StatefulBase.__init__(self, **kwargs)
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.ext_host = ext_host
        self.ext_port = ext_port
        self.loop = None
        self.is_ready = Event()

    def state(self):
        return dict(ext_host=self.ext_host, ext_port=self.ext_port)

    def create_app(self, routes: Dict[Route, Tuple[str, str, Callable]]):
        """
        function to run a web server given a dictionary of routes

        :param routes: {Route => (method, path, function}
        :return:
        """
        raise NotImplementedError

    async def ask(self, req: Request) -> Response:
        """ makes a request to the external host """
        raise NotImplementedError

    async def forward(self, req: Request):
        """ forward a request to the external host """
        raise NotImplementedError

    def run(self):
        """ start the server thread """
        raise NotImplementedError

    def exit(self):
        """ stop the server thread """
        raise NotImplementedError


