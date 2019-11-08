import re

from neural_rerank.testing import RegexDict
import unittest


class TestRegexDict(unittest.TestCase):
    def setUp(self):
        self.base_dict = {
            'applesauce': 10,
            'grapple': 7,
            'happily': 7
        }

    def test_construction(self):
        redict = RegexDict(self.base_dict)
        self.assertEqual(len(redict), 3)
        self.assertDictEqual(redict, self.base_dict)

    def test_slice_syntax(self):
        redict = RegexDict(self.base_dict)
        self.assertListEqual(sorted(redict[:'app':]),
                             [('applesauce', 10), ('grapple', 7), ('happily', 7)])
        self.assertListEqual(sorted(redict[:'.app':]),
                             [('grapple', 7), ('happily', 7)])
        self.assertListEqual(sorted(redict[:'apple':]),
                             [('applesauce', 10), ('grapple', 7)])
        # Test flags in slice as well
        self.assertListEqual(sorted(redict[:'.APP':re.I]),
                             [('grapple', 7), ('happily', 7)])

    def test_re_compiled(self):
        redict = RegexDict(self.base_dict)
        app = re.compile('.app')
        self.assertListEqual(sorted(redict[:app:]), sorted(redict[:'.app':]))

    def test_in_operator(self):
        redict = RegexDict(self.base_dict)
        # Non-regex string keys
        self.assertIn('grapple', redict)
        # Pre-compiled re objects
        app = re.compile('.app')
        self.assertIn(app, redict)
        bad = re.compile('ba+d')
        self.assertNotIn(bad, redict)

    def test_setitem(self):
        redict = RegexDict(self.base_dict)
        # regular setitem
        redict['grapple'] = 8
        self.assertEqual(redict['grapple'], 8)
        # regex setitem
        redict[:'apple':] = 1
        self.assertListEqual(sorted(redict[:'app':]),
                             [('applesauce', 1), ('grapple', 1), ('happily', 7)])

    def test_delitem(self):
        redict = RegexDict(self.base_dict)
        # regular delitem
        del redict['grapple']
        self.assertNotIn('grapple', redict)
        # regex delitem
        del redict[:'ily':]
        self.assertDictEqual(redict, dict(applesauce=10))
