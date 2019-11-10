from nboost.model import TransformersModel
from nboost.base.types import *
from nboost.paths import RESOURCES
from unittest.case import SkipTest
from pathlib import Path
import unittest
import asyncio


class TestTransformersModel(unittest.TestCase):

    def setUp(self):
        if not Path('./marco_bert').is_dir():
            raise SkipTest('./marco_bert not found')
        self.model = TransformersModel()
        self.query = Query('O wherefore art thou')
        self.choices = Choices()

        with RESOURCES.joinpath('sonnets_small.txt').open() as fh:
            for i, line in enumerate(fh):
                if not line == '':
                    self.choices.append(line.encode())

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
