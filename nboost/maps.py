
# component => class => module
CLASS_MAP = {
    'models': {
        'ShuffleModel': 'shuffle',
        'TransformersModel': 'transformers',
        'BertModel': 'bert_model',
        'AlbertModel': 'albert_model'
    },
    'indexers': {
        'ESIndexer': 'es'
    }
}

# model_dir => url
MODEL_MAP = {
    "bert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/bert-base-uncased-msmarco.tar.gz",
    "albert-tiny-uncased-msmarco": "https://storage.googleapis.com/koursaros/albert-tiny-uncased-msmarco.tar.gz",
    "biobert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/biobert-base-uncased-msmarco.tar.gz",
    "pt-tinybert-msmarco": "https://storage.googleapis.com/koursaros/pt-tinybert-msmarco.tar.gz",
    "pt-bert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/pt-bert-base-uncased-msmarco.tar.gz"
}

# image => directory
IMAGE_MAP = {
    'alpine': '../Dockerfiles/alpine',
    'tf': '../Dockerfiles/tf',
    'torch': '../Dockerfiles/torch'
}

CONFIG_MAP = {
    'elasticsearch': {
        'query_path': '(body.query.match) | (body.query.term.*) | ($.url.query.q)',
        'topk_path': '(body.size) | (url.query.size)',
        'cvalues_path': '$.body.hits.hits[*]._source.*',
        'true_cids_path': '$.body.nboost.cids',
        'cids_path': '$.body.hits.hits[*]._id',
        'choices_path': '$.body.hits.hits',
        'capture_path': '/.*/_search',
        'default_topk': 10
    }
}
