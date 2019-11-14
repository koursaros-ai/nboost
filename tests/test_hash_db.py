from nboost.base.types import *
from nboost.db.hash import HashDb
import unittest


class TestHashDb(unittest.TestCase):
    def test_hash_db(self):
        db = HashDb()
        q = Query(b'test query')
        c = [Choice(b'choice'), Choice(b'another choice')]
        db.save(q, c)
        self.assertEqual(len(c), len(db.choices))

        query, choices = db.get(q.ident, [choice.ident for choice in c])
        self.assertEqual(q.ident, query.ident)
        self.assertEqual(q.body, query.body)

        for i, choice in enumerate(choices):
            self.assertEqual(c[i].ident, choice.ident)
            self.assertEqual(c[i].body, choice.body)


