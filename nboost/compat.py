from nboost.maps import CLASS_MAP, URL_MAP, MODULE_MAP


class BackwardsCompatibility:
    """Augment global modules to be backwards compatible"""
    def set(self):
        MODULE_MAP['QAModel'] = MODULE_MAP['QAModelPlugin']
        MODULE_MAP['RerankModel'] = MODULE_MAP['RerankModelPlugin']
        MODULE_MAP['ShuffleModel'] = MODULE_MAP['ShuffleRerankModelPlugin']
        MODULE_MAP['PtBertModel'] = MODULE_MAP['PtBertRerankModelPlugin']
        MODULE_MAP['TfBertModel'] = MODULE_MAP['TfBertRerankModelPlugin']
        MODULE_MAP['TfAlbertModel'] = MODULE_MAP['TfAlbertRerankModelPlugin']
        MODULE_MAP['PtDistilBertQAModel'] = MODULE_MAP['PtDistilBertQAModelPlugin']
        URL_MAP["bert-base-uncased-msmarco"] = URL_MAP["tf-bert-base-uncased-msmarco"]
        URL_MAP["albert-tiny-uncased-msmarco"] = URL_MAP["tf-albert-tiny-uncased-msmarco"]
        URL_MAP["biobert-base-uncased-msmarco"] = URL_MAP["tf-biobert-base-uncased-msmarco"]
        CLASS_MAP["bert-base-uncased-msmarco"] = CLASS_MAP["tf-bert-base-uncased-msmarco"]
        CLASS_MAP["albert-tiny-uncased-msmarco"] = CLASS_MAP["tf-albert-tiny-uncased-msmarco"]
        CLASS_MAP["biobert-base-uncased-msmarco"] = CLASS_MAP["tf-biobert-base-uncased-msmarco"]
