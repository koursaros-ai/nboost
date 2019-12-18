from nboost.proxy import Proxy
import unittest


class TestPtFilterModel(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy(model_dir='pt-bert-base-uncased-msmarco', filter_results=True)

    def test_rank(self):
        ranks = self.proxy.model.rank('His tender heir', CHOICES)
        self.assertEqual(self.proxy.model.__class__.__name__, 'PtBertModel')
        self.assertIsInstance(ranks, list)
        self.assertEqual(1, len(ranks))

        ranks = self.proxy.model.rank('His tender heir', CHOICES[:1])
        self.assertEqual(self.proxy.model.__class__.__name__, 'PtBertModel')
        self.assertIsInstance(ranks, list)
        self.assertEqual(0, len(ranks))

    def tearDown(self) -> None:
        self.proxy.model.close()


CHOICES = [
    'From fairest creatures we desire increase',
    'That thereby beautys rose might never die',
    'But as the riper should by time decease',
    'His tender heir might bear his memory:',
    'But thou contracted to thine own bright eyes',
    'Feedst thy lights flame with self-substantial fuel',
]