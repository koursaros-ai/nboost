"""General nboost package parameters"""
from pathlib import Path

PKG_PATH = Path(__file__).parent

# component => class => module
CLASS_MAP = {
    'codex': {
        'ESCodex': 'es'
    },
    'model': {
        'ShuffleModel': 'shuffle',
        'TransformersModel': 'transformers',
        'BertModel': 'bert_model',
        'AlbertModel': 'albert_model'
    }
}

# model_dir => url
MODEL_MAP = {
    "bert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/bert-base-uncased-msmarco.tar.gz",
    "albert-tiny-uncased-msmarco": "https://storage.googleapis.com/koursaros/albert-tiny-uncased-msmarco.tar.gz",
    "biobert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/biobert-base-uncased-msmarco.tar.gz"
}

# image => directory
IMAGE_MAP = {
    'alpine': '../Dockerfiles/alpine',
    'tf': '../Dockerfiles/tf',
    'torch': '../Dockerfiles/torch'
}

# dataset => file_type => (file_name, [id column, data column], delimiter)
# url: compressed url location of dataset
# size: rough number of rows in the dataset (used to check if index exists)
DATASET_MAP = {
    'ms_marco': {
        'qrels': ('qrels.dev.small.tsv', [0, 2], '\t'),
        'queries': ('queries.dev.tsv', [0, 1], '\t'),
        'choices': ('collection.tsv', [0, 1], '\t'),
        'url': 'https://msmarco.blob.core.windows.net/msmarcoranking/collectionandqueries.tar.gz',
        'size': 8 * 10 ** 6
    }
}
