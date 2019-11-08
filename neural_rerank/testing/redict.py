"""
I got this from regexdict.py (and made some alterations):

regexdict.py - Dictionary with support for regular expression searching.
CJ Carey - perimosocordiae@github
Daryl Koopersmith - koop@github
"""
import re


class RegexDict(dict):

    def __filter_matches(self, regex):
        return (k for k in self if _is_match(regex, k))

    def __contains__(self, key):
        if not hasattr(key, 'search'):
            return dict.__contains__(self, key)
        return any(True for _ in self.__filter_matches(key))

    def __getitem__(self, key):
        regex = _unslice(key)
        if regex is None:
            return dict.__getitem__(self, key)
        kv_iter = ((k, dict.__getitem__(self, k))
                   for k in self.__filter_matches(regex))
        return kv_iter

    def __setitem__(self, key, value):
        regex = _unslice(key)
        if regex is None:
            return dict.__setitem__(self, key, value)
        for k in self.__filter_matches(regex):
            dict.__setitem__(self, k, value)

    def __delitem__(self, key):
        regex = _unslice(key)
        if regex is None:
            return dict.__delitem__(self, key)
        # Force list to avoid mutation during iteration.
        for k in list(self.__filter_matches(regex)):
            dict.__delitem__(self, k)

    # Python2 compatibility functions
    def __getslice__(self, start, stop):
        return self.__getitem__(slice(start, stop))

    def __setslice__(self, start, stop):
        return self.__setitem__(slice(start, stop))

    def __delslice__(self, start, stop):
        return self.__delitem__(slice(start, stop))


def _unslice(key):
    if not isinstance(key, slice):
        return None
    # slices have the form [:pattern:flags]
    if key.start is not None:
        raise ValueError('Regex sugar must have the form [:pattern:flags]')
    flags = 0 if key.step is None else key.step
    return re.compile(key.stop, flags=flags)


def _is_match(regex, s):
    try:
        return regex.search(s) is not None
    except TypeError:
        return False