
from typing import Dict, Tuple, Callable
from threading import Thread, Event
from ..base import StatefulBase
from ..base.types import *
import asyncio


class BaseServer(StatefulBase, Thread):
    """The server implements routes that route paths designated by the codex.
    During initialization, the proxy hands the route dictionary to the server
    to execute when it receives a request.

    The server is expected to proxy all unexpected routes to the server api
    and back to the client.
    """
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
        self.is_ready = Event()

        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            self.asyncio.set_event_loop(self.loop)

    def state(self):
        return dict(ext_host=self.ext_host, ext_port=self.ext_port)

    def create_app(self,
                   routes: Dict[Route, Tuple[Dict[str, List[str]], Callable]]):
        """function to run a web server given a dictionary of routes

        :param routes: {Route => ({path => [methods]}, function)
        """
        raise NotImplementedError

    async def run_app(self):
        """Run the server """

    async def close(self):
        """ Close and clean up the server. Called after close() is called on
        the proxy object containing the server."""
        raise NotImplementedError

    # SEARCH METHOD
    async def ask(self, req: Request) -> Response:
        """ Make the magnified request to the server api. """
        raise NotImplementedError

    async def forward(self, req: Request):
        """ forward a request to the external host """
        raise NotImplementedError

    def run(self):
        self.logger.critical('STARTING')
        self.loop.run_until_complete(self.run_app())
        self.is_ready.set()
        self.loop.run_forever()
        self.logger.critical('LOOP STOPPED')
        self.is_ready.clear()

    def stop(self):
        self.logger.critical('CLOSING')
        wait = asyncio.run_coroutine_threadsafe(self.close(), self.loop)
        wait.result()
        self.logger.critical('STOPPING LOOP')
        self.loop.call_soon_threadsafe(self.loop.stop)

