from typing import Tuple, Callable, Iterable, Any
from threading import Thread, Event
from .base import StatefulBase
from .types import *
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
        self.id = '%s:%s->%s:%s' % (host, port, ext_host, ext_port)
        self.is_ready = Event()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def state(self):
        return dict(ext_host=self.ext_host, ext_port=self.ext_port)

    def create_app(self,
                   routes: Iterable[Tuple[bytes, List[bytes], Callable]],
                   not_found_handler: Callable):
        """function to run a web server given a dictionary of routes. Instead
        of handling 404 cases within the server, call the not_found handlers
        for tracking proxy speeds.

        :param routes: iter of (path , methods, function). These routes
            are specific to search, train, and status routes but should be
            kept modular for testing purposes.
        :param not_found_handler: calls the forward() method on the server but
            also tracks the speed for benchmarking purposes.
        """
        raise NotImplementedError

    async def run_app(self):
        """Run the server """
        raise NotImplementedError

    async def close(self):
        """ Close and clean up the server. Called after close() is called on
        the proxy object containing the server."""
        raise NotImplementedError

    # SEARCH METHOD
    async def ask(self, req: Request) -> Response:
        """ Make the magnified request to the server api. """
        raise NotImplementedError

    async def forward(self, req: Any) -> Any:
        """ forward a request to the external host """
        raise NotImplementedError

    def run(self):
        self.logger.critical('STARTING PROXY')
        self.loop.run_until_complete(self.run_app())
        self.is_ready.set()
        self.logger.critical('LISTENING: %s' % self.id)
        self.loop.run_forever()
        self.is_ready.clear()

    def stop(self):
        self.logger.critical('STOPPING PROXY')
        asyncio.run_coroutine_threadsafe(self.close(), self.loop).result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.logger.critical('CLOSED: %s' % self.id)
