from neural_rerank.models import DBERTRank
from tests.paths import RESOURCES
import unittest
import asyncio


class TestDBERTRank(unittest.TestCase):

    def setUp(self):
        self.model = DBERTRank()
        self.query = 'O wherefore art thou'
        self.candidates = []

        with RESOURCES.joinpath('sonnets_small.txt').open() as fh:
            for line in fh:
                if not line == '':
                    self.candidates.append(line)

    def test_train(self):
        labels = [float(i % 2) for i in range(len(self.candidates))]
        res = (
            asyncio.get_event_loop()
            .run_until_complete(self.model.train(self.query, self.candidates, labels=labels))
        )
        self.assertIsInstance(res, list)

    def test_rank(self):
        res = (
            asyncio.get_event_loop()
            .run_until_complete(self.model.rank(self.query, self.candidates))
        )
        self.assertIsInstance(res, list)
