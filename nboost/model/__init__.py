from .transformers import TransformersModel
from .base import BaseModel
from .test import TestModel
from .bert_marco import BertMarcoModel

MODEL_PATHS = {
    "tf_bert_marco" : {
        "url" : "https://storage.googleapis.com/koursaros/bert_marco.tar.gz",
        "ckpt" : "bert_marco/bert_model.ckpt"
    }
}
