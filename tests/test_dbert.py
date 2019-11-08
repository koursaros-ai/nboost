from neural_rerank.model import DBERTModel
from neural_rerank.base.types import *
from tests.paths import RESOURCES
import unittest
import asyncio


class TestDBERTModel(unittest.TestCase):

    def setUp(self):
        self.model = DBERTModel()
        self.query = Query('O wherefore art thou')
        self.choices = []

        with RESOURCES.joinpath('sonnets_small.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(Choice(i, line))

    def test_train(self):
        labels = Labels(float(i % 2) for i in range(len(self.choices)))
        res = (
            asyncio.get_event_loop()
            .run_until_complete(self.model.train(self.query, self.choices, labels=labels))
        )

    def test_rank(self):
        res = (
            asyncio.get_event_loop()
            .run_until_complete(self.model.rank(self.query, self.choices))
        )
        self.assertIsInstance(res, list)
