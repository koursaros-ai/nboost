# from nboost.plugins.models import resolve_model
# from nboost import defaults
# import unittest
# import numpy as np
#
#
# class TestPtBertRerankModelPlugin(unittest.TestCase):
#     def setUp(self):
#         self.model = resolve_model(
#             model_dir='onnx-bert-base-msmarco',
#             data_dir=defaults.data_dir,
#             model_cls=''
#         )
#         self.pt_model = resolve_model(
#             model_dir='pt-bert-base-uncased-msmarco',
#             data_dir=defaults.data_dir,
#             model_cls=''
#         )
#
#     def test_rank(self):
#         QUERY = 'O wherefore art thou'
#         ranks, scores = self.model.rank(QUERY, CHOICES)
#         self.assertEqual(self.model.__class__.__name__, 'ONNXBertRerankModelPlugin')
#         self.assertIsInstance(ranks, list)
#         self.assertEqual(6, len(ranks))
#         pt_ranks, pt_scores = self.pt_model.rank(QUERY, CHOICES)
#         assert np.allclose(pt_scores, scores, rtol=1e-04, atol=1e-05)
#
#     def tearDown(self) -> None:
#         self.model.close()


CHOICES = [
    'From fairest creatures we desire increase' * 4,
    'That thereby beautys rose might never die' * 4,
    'But as the riper should by time decease' * 4,
    'His tender heir might bear his memory:' * 4,
    'But thou contracted to thine own bright eyes' * 4,
    'Feedst thy lights flame with self-substantial fuel' * 4,
]