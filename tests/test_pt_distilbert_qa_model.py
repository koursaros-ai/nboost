import unittest
from nboost.proxy import Proxy


class TestPtDistilBertQAModel(unittest.TestCase):

    def setUp(self):
        self.proxy = Proxy(qa_model_dir='distilbert-base-uncased-distilled-squad',
                           qa_model='PtDistilBertQAModel', max_seq_length=32, qa=True)

    def test_rank(self):
        QUESTION = 'Who bears his memory?'
        answer, offsets, score = self.proxy.qa_model.get_answer(QUESTION, CONTEXT)
        self.assertEqual(answer, 'His tender heir')
        start_char, end_char, passage = offsets
        self.assertEqual(answer, CONTEXT[start_char:end_char])

    def test_long_rank(self):
        QUESTION = 'Who contracted to thine own bright eyes?'
        answer, offsets, score = self.proxy.qa_model.get_answer(QUESTION*10, CONTEXT)
        self.assertEqual(answer, 'thou contracted to thine own bright eyes')

    def tearDown(self) -> None:
        self.proxy.qa_model.close()


CONTEXT = 'His tender heir might bear his memory, but thou contracted to thine own bright eyes'
