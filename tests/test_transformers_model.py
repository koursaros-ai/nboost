from nboost.model.transformers import TransformersModel
from tests import RESOURCES
import unittest
from nboost.types import Choice


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = TransformersModel(model_dir='distilbert-base-uncased')
        self.query = 'O wherefore art thou'
        self.choices = []

        with RESOURCES.joinpath('sonnets.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(Choice('0', line.encode()))

    def test_rank(self):
        self.model.rank(self.query.encode(), self.choices)
        self.assertIsInstance(self.choices, list)
