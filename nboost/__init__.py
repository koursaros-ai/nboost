from pathlib import Path

__version__ = '0.0.1-rc-1'

PKG_PATH = Path(__file__).parent

# component => class => module
CLASS_MAP = {
    'codex': {
        'TestCodex': 'test',
        'ESCodex': 'es'
    },
    'db': {
        'HashDb': 'hash'
    },
    'server': {
        'AioHttpServer': 'aio',
        'LoopServer': 'loop'
    },
    'model': {
        'TestModel': 'test',
        'TransformersModel': 'transformers',
        'BertModel': 'bert_model'
    }
}

# model_dir => url
MODEL_MAP = {
    "bert-base-uncased-msmarco'": "https://storage.googleapis.com/koursaros/bert_marco.tar.gz"
}