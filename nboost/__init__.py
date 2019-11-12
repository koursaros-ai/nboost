__version__ = '0.0.1-rc-1'

from pathlib import Path

BASE = Path(__file__).absolute().parent
RESOURCES = BASE.joinpath('resources')


class_map = {
    'codex': {
        'TestCodex': 'test',
        'ESCodex': 'es'
    },
    'db': {
        'HashDb': 'hash'
    },
    'server': {
        'AioHttpServer': 'aio'
    },
    'model': {
        'TestModel': 'test',
        'TransformersModel': 'transformers'
    }
}
