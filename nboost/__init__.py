"""General nboost package parameters"""
from pathlib import Path

__version__ = '0.0.3'

PKG_PATH = Path(__file__).parent

# component => class => module
CLASS_MAP = {
    'protocol': {
        'TestCodex': 'test',
        'ESProtocol': 'es'
    },
    'model': {
        'TestModel': 'test',
        'TransformersModel': 'transformers',
        'BertModel': 'bert_model',
        'AlbertModel': 'albert_model'
    }
}

# model_dir => url
MODEL_MAP = {
    "bert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/bert-base-uncased-msmarco.tar.gz",
    "albert-tiny-uncased-msmarco": "https://storage.googleapis.com/koursaros/albert-tiny-uncased-msmarco.tar.gz"
}

# image => directory
IMAGE_MAP = {
    'alpine': '../Dockerfiles/alpine',
    'tf': '../Dockerfiles/tf',
    'torch': '../Dockerfiles/torch'
}
