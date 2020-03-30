
# class => module
MODULE_MAP = {
    'ShuffleRerankPlugin': 'plugins.rerank.shuffle',
    'PtTransformersRerankPlugin': 'plugins.rerank.transformers',
    'PtDistilBertQAModelPlugin': 'plugins.qa.distilbert'
}

# image => directory
IMAGE_MAP = {
    'alpine': '../Dockerfiles/alpine',
    'pt': '../Dockerfiles/pt'
}

INDEXER_MAP = {
    'ESIndexer': 'indexers.es'
}
