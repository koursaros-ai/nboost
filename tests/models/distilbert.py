from models.distilbert import DBRank
import unittest
import os

class TestDistilibert(unittest.TestCase):

    def setUp(self):
        self.model = DBRank()
        self.query = 'O wherefore art thou'
        self.candidates = []

        with open(os.path.join(os.path.dirname(__file__), 'sonnets_small.txt')) as f:
            for line in f:
                if not line == '':
                    self.candidates.append(line)

    def test_train(self):
        self.model(self.query,
                   self.candidates,
                   labels = [float(i % 2) for i in range(len(self.candidates))])

    def test_rank(self):
        res = self.model(self.query, self.candidates, k=5)
        self.assertIsInstance(res, list)
