from nboost.model.bert_model import BertModel
from nboost.base.types import *
from tests import RESOURCES
import unittest


class TestTransformersModel(unittest.TestCase):

    def setUp(self):
        self.model = BertModel()
        self.query = Query(b'O wherefore art thou')
        self.choices = []

        with RESOURCES.joinpath('sonnets.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(Choice(line.encode()))

    def test_rank(self):
        self.model.rank(self.query, self.choices)
        self.assertIsInstance(self.choices[0].rank, int)
