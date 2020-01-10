"""Socket server"""
from threading import Thread, Event, get_ident
from typing import Tuple
import socket
from nboost.logger import set_logger
from nboost import defaults


class SocketServer(Thread):
    """Base Socket Server class for the proxy"""

    def __init__(self, host: type(defaults.host) = defaults.host,
                 port: type(defaults.port) = defaults.port,
                 backlog: type(defaults.backlog) = defaults.backlog,
                 workers: type(defaults.workers) = defaults.workers,
                 verbose: type(defaults.verbose) = defaults.verbose,
                 **kwargs):
        super().__init__()
        self.address = (socket.gethostbyname(host), port)
        self.backlog = backlog
        self.workers = workers
        self.is_ready = Event()
        self.sock = self.set_socket()
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)

    @staticmethod
    def set_socket() -> socket.socket:
        """Construct a reuseable socket address"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def worker(self):
        """Socket loop for each worker"""
        try:
            while True:
                self.loop(*self.sock.accept())

        except OSError:
            self.logger.debug('Closing worker %s...', get_ident())

    def loop(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Loop for each worker to execute when it receives client conn"""

    def run(self):
        """Run the socket server main thread"""
        self.sock.bind(self.address)
        self.sock.listen(self.backlog)
        threads = []

        try:
            self.logger.info('Starting %s workers...', self.workers)
            for _ in range(self.workers):
                thread = Thread(target=self.worker)
                thread.start()
                threads.append(thread)

            self.is_ready.set()
            self.logger.critical('Listening on %s:%s...', *self.address)
            for thread in threads:
                thread.join()

        finally:
            self.logger.critical('Closed %s:%s...', *self.address)

    def close(self):
        """Close the serving socket"""
        self.logger.info('Closing %s:%s...', *self.address)
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.join()
