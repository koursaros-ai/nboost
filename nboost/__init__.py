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
        'AioHttpServer': 'aio'
    },
    'model': {
        'TestModel': 'test',
        'TransformersModel': 'transformers',
        'MarcoBertModel': 'bert_marco'
    }
}

# pretrained => finetuned => (url, model_dir)
MODEL_MAP = {
    "bert_model": {
        "bert_marco": "https://storage.googleapis.com/koursaros/bert_marco.tar.gz"
    }
}