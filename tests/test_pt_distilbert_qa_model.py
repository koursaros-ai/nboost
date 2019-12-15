import unittest
from nboost.proxy import Proxy


class TestPtDistilBertQAModel(unittest.TestCase):

    def setUp(self):
        self.proxy = Proxy(qa_model_dir='distilbert-base-uncased-distilled-squad',
                           qa_model='PtDistilBertQAModel', qa=True)

    def test_rank(self):
        answer, _ = self.proxy.qa_model.get_answer('Who bears his memory?', CONTEXT)
        self.assertEqual(answer, 'His tender')

    def tearDown(self) -> None:
        self.proxy.qa_model.close()


CONTEXT = 'His tender heir might bear his memory, but thou contracted to thine own bright eyes'
