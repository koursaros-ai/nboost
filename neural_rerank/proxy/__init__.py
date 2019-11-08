from ..base import StatefulBase
from ..codex import BaseCodex
from ..model import BaseModel
from ..server import BaseServer
from ..db import BaseDb
from ..base.types import *
from typing import Type, Tuple, Dict, List, Any
from inspect import isawaitable
import json as JSON
import time


class Proxy(StatefulBase):
    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 53001,
                 ext_host: str = '127.0.0.1',
                 ext_port: int = 54001,
                 lr: float = 10e-3,
                 data_dir: str = '/.cache',
                 multiplier: int = 10,
                 field: str = None,
                 read_bytes: int = 2048,
                 server: Type[BaseServer] = BaseServer,
                 model: Type[BaseModel] = BaseModel,
                 codex: Type[BaseCodex] = BaseCodex,
                 db: Type[BaseDb] = BaseDb, **kwargs):
        super().__init__(**kwargs)

        server = server(
            host=host,
            port=port,
            ext_host=ext_host,
            ext_port=ext_port,
            read_bytes=read_bytes)
        model = model(lr=lr, data_dir=data_dir)
        codex = codex(multiplier=multiplier, field=field)
        db = db()

        def track(f: Any):
            cls = f.__self__.__class__.__name__ if hasattr(f, '__self__') else self.__class__.__name__
            ident = (cls, f.__name__)

            async def decorator(*args):
                start = time.perf_counter()
                res = f(*args)
                ret = await res if isawaitable(res) else res
                ms = (time.perf_counter() - start) * 1000
                db.lap(ms, *ident)
                return ret
            return decorator

        @track
        async def search(_1: Request) -> Response:
            _2: Request = await track(codex.magnify)(_1)
            _3: Response = await track(server.ask)(_2)
            _4: Tuple[Query, List[Choice]] = await track(codex.parse)(_1, _3)
            await track(db.save)(*_4)
            _5: Ranks = await track(model.rank)(*_4)
            _6: Response = await track(codex.pack)(_1, _3, *_4, _5)
            return _6

        @track
        async def train(_1: Request) -> Response:
            _2: Cid = await track(codex.pluck)(_1)
            _3: Tuple[Query, List[Choice], Labels] = await track(db.get)(_2)
            await track(model.train)(*_3)
            _4: Response = await track(codex.ack)(_2)
            return _4

        @track
        async def status(_1: Request) -> Response:
            _2: Dict = await track(server.chain_state)({})
            _3: Dict = await track(codex.chain_state)(_2)
            _4: Dict = await track(model.chain_state)(_3)
            _5: Dict = await track(db.chain_state)(_4)
            _6: Dict = await track(self.chain_state)(_5)
            _7: Response = await track(codex.pulse)(_6)
            return _7

        @track
        async def not_found(_1: Request) -> Response:
            _2: Response = await track(server.forward)(_1)
            return _2

        @track
        async def error(_1: Exception) -> Response:
            _2: Response = await track(codex.catch)(_1)
            return _2

        self.routes = {
            Route.SEARCH: (codex.SEARCH_METHOD, codex.SEARCH_PATH, search),
            Route.TRAIN: (codex.TRAIN_METHOD, codex.TRAIN_PATH, train),
            Route.STATUS: (codex.STATUS_METHOD, codex.STATUS_PATH, status),
            Route.NOT_FOUND: (codex.NOT_FOUND_METHOD, codex.NOT_FOUND_PATH, not_found),
            Route.ERROR: (codex.ERROR_METHOD, codex.ERROR_PATH, error)
        }

        self.server = server
        self.codex = codex
        self.db = db
        self.model = model
        self.is_ready = server.is_ready
        self.logger.info(JSON.dumps(dict(
            server=server.__class__.__name__,
            codex=codex.__class__.__name__,
            model=model.__class__.__name__,
            db=db.__class__.__name__,
        ), indent=4))

    def enter(self):
        self.server.create_app(self.routes)
        self.server.start()

    def exit(self):
        self.logger.critical('Stopping proxy...')
        self.server.exit()

    def __enter__(self):
        self.enter()
        self.is_ready.wait()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()

    # def state(self):
    #     return dict(
    #         server=self.server,
    #         codex=self.codex,
    #         db=self.db,
    #         model=self.model
    #     )

