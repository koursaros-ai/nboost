from nboost.model.bert_marco import BertMarcoModel
from nboost.base.types import *
from tests import RESOURCES
import unittest
import os


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = BertMarcoModel(model_ckpt='bert_base_msmarco')
        self.query = Query('O wherefore art thou'.encode())
        self.choices = Choices()

        with RESOURCES.joinpath('sonnets.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(line.encode())

    def test_rank(self):
        res = self.model.rank(self.query, self.choices)
        self.assertIsInstance(res, list)
