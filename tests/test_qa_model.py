import unittest
from nboost.models.torch_models.distilbert_qa import TorchDistilBertQAModel


class TestTfBertModel(unittest.TestCase):

    def setUp(self):
        self.model = TorchDistilBertQAModel()

    def test_rank(self):
        answer, _ = self.model.get_answer('who bears his memory?', CONTEXT)
        self.assertEqual(answer, 'His tender')

    def tearDown(self) -> None:
        self.model.close()


CONTEXT = 'His tender heir might bear his memory, but thou contracted to thine own bright eyes'
