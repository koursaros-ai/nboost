from nboost.model.transformers import TransformersModel
from nboost.base.types import *
from tests import RESOURCES
import unittest
import asyncio


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = TransformersModel(model_dir='distilbert-base-uncased')
        self.query = Query('O wherefore art thou'.encode())
        self.choices = []

        with RESOURCES.joinpath('sonnets.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(Choice(line.encode()))

    @unittest.SkipTest
    def test_train(self):
        for i, choice in enumerate(self.choices):
            choice.label = i % 2

        asyncio.get_event_loop().run_until_complete(
            self.model.train(self.query, self.choices))

    def test_rank(self):
        asyncio.get_event_loop().run_until_complete(
            self.model.rank(self.query, self.choices))
        self.assertIsInstance(self.choices[0].rank, int)
