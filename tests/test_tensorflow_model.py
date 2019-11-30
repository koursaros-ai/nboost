from nboost.model.bert_model import BertModel
from tests import RESOURCES
import unittest


class TestTransformersModel(unittest.TestCase):

    def setUp(self):
        self.model = BertModel()
        self.query = b'O wherefore art thou'
        self.choices = []

        with RESOURCES.joinpath('sonnets.txt').open('rb') as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(line)

    def test_rank(self):
        self.model.rank(self.query, self.choices)
        self.assertIsInstance(self.choices, list)

    def tearDown(self) -> None:
        self.model.close()
