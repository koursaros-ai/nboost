from nboost.plugins.models import resolve_model
from nboost import defaults
import unittest


class TestPtDistilBertQAModel(unittest.TestCase):

    def setUp(self):
        self.qa_model = resolve_model(
            model_dir='distilbert-base-uncased-distilled-squad',
            data_dir=defaults.data_dir,
            model_cls='PtDistilBertQAModelPlugin',
            max_seq_length = 32
        )

    def test_rank(self):
        QUESTION = 'Who bears his memory?'
        answer, start_pos, end_pos, score = self.qa_model.get_answer(QUESTION, CONTEXT)
        self.assertEqual(answer, 'His tender heir')
        self.assertEqual(answer, CONTEXT[start_pos:end_pos])

    def test_long_rank(self):
        QUESTION = 'Who contracted to thine own bright eyes?'
        answer, start_pos, end_pos, score = self.qa_model.get_answer(QUESTION*10, CONTEXT)
        self.assertEqual(answer, '')
        answer, start_pos, end_pos, score = self.qa_model.get_answer(QUESTION, CONTEXT)
        self.assertEqual(answer, 'His tender heir might bear his memory, but thou')

    def test(self):
        QUESTION = 'maps site:smallwebsite.us'
        CONTEXT = '''High School ReUnion Small Website – including a custom memorable High School ReUnion domain name. Bring old classmates together with an awesome class reunion website. For $500 you get a custom School ReUnion domain name, a 5 Page secure (httpS) website with maps, and a TEXT widget to capture re-union staff – TEXT Messages – […]'''
        answer, start_pos, end_pos, score = self.qa_model.get_answer(QUESTION, CONTEXT)
        QUESTION = 'relax'
        CONTEXT = '''High School ReUnion Small Website – including a custom memorable High School ReUnion domain name. Bring old classmates together with an awesome class reunion website. For $500 you get a custom School ReUnion domain name, a 5 Page secure (httpS) website with maps, and a TEXT widget to capture re-union staff – TEXT Messages – […]'''
        answer, start_pos, end_pos, score = self.qa_model.get_answer(QUESTION, CONTEXT)

    def tearDown(self) -> None:
        self.qa_model.close()


CONTEXT = 'His tender heir might bear his memory, but thou contracted to thine own bright eyes'
