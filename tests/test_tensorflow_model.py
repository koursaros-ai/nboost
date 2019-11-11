from nboost.model import BertMarcoModel
from nboost.base.types import *
from paths import RESOURCES
import unittest
import asyncio
import os


class TestModel(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('bert_marco/bert_config.json'):
            raise unittest.SkipTest("Skipping BERT marco test, model binary not found")
        self.model = BertMarcoModel(model_ckpt='bert_marco/bert_model.ckpt')
        self.query = Query('O wherefore art thou'.encode())
        self.choices = Choices()

        with RESOURCES.joinpath('sonnets_small.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(line.encode())

    def test_rank(self):
        res = self.model.rank(self.query, self.choices)
        self.assertIsInstance(res, list)
