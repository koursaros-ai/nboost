
# class => module
MODULE_MAP = {
    'QAModel': 'models.qa.base',
    'RerankModel': 'models.rerank.base',
    'ShuffleModel': 'models.rerank.shuffle',
    'PtBertModel': 'models.rerank.pt.bert',
    'TfBertModel': 'models.rerank.tf.bert',
    'TfAlbertModel': 'models.rerank.tf.albert',
    'PtDistilBertQAModel': 'models.qa.pt.distilbert',
}

CLASS_MAP = {
    "pt-tinybert-mrpc": "PtBertModel",
    "pt-tinybert-msmarco": "PtBertModel",
    "pt-bert-base-uncased-msmarco": "PtBertModel",
    "tf-bert-base-uncased-msmarco": "TfBertModel",
    "tf-albert-tiny-uncased-msmarco": "TfAlbertModel",
    "tf-biobert-base-uncased-msmarco": "TfBertModel"
}

URL_MAP = {
    "tf-bert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/tf-bert-base-uncased-msmarco.tar.gz",
    "tf-albert-tiny-uncased-msmarco": "https://storage.googleapis.com/koursaros/albert-tiny-uncased-msmarco.tar.gz",
    "tf-biobert-base-uncased-msmarco": "https://storage.googleapis.com/koursaros/biobert-base-uncased-msmarco.tar.gz",
    "pt-tinybert-msmarco": "https://storage.googleapis.com/koursaros/pt-tinybert-msmarco.tar.gz",
    "pt-bert-base-uncased-msmarco":  "https://storage.googleapis.com/koursaros/pt-bert-base-uncased-msmarco.tar.gz",
    "pt-tinybert-mrpc" : "https://storage.googleapis.com/koursaros/pt-tinybert-mrpc.tar.gz",
}

# backwards compatibility (before we added tf/pt)
CLASS_MAP["bert-base-uncased-msmarco"] = CLASS_MAP["tf-bert-base-uncased-msmarco"]
CLASS_MAP["albert-tiny-uncased-msmarco"] = CLASS_MAP["tf-albert-tiny-uncased-msmarco"]
CLASS_MAP["biobert-base-uncased-msmarco"] = CLASS_MAP["tf-biobert-base-uncased-msmarco"]
URL_MAP["bert-base-uncased-msmarco"] = URL_MAP["tf-bert-base-uncased-msmarco"]
URL_MAP["albert-tiny-uncased-msmarco"] = URL_MAP["tf-albert-tiny-uncased-msmarco"]
URL_MAP["biobert-base-uncased-msmarco"] = URL_MAP["tf-biobert-base-uncased-msmarco"]

# image => directory
IMAGE_MAP = {
    'alpine': '../Dockerfiles/alpine',
    'tf': '../Dockerfiles/tf',
    'pt': '../Dockerfiles/pt'
}

INDEXER_MAP = {
    'ESIndexer': 'indexers.es'
}
