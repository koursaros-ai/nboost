from nboost.base.types import *
from nboost.db.hash import HashDb
import unittest


class TestHashDb(unittest.TestCase):
    def test_hash_db(self):
        db = HashDb()
        q = Query(b'test query')
        c = Choices([b'choice', b'another choice'])
        qid, cids = db.save(q, c)
        self.assertEqual(len(c), len(cids))

        query, choices, labels = db.get(qid, cids)
        self.assertEqual(q, query)
        self.assertEqual(c, choices)
        self.assertEqual(labels, [1.0, 1.0])


