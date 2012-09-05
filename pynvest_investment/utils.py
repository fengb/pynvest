import operator
import bisect


# FIXME: RENAME PLEASE
class BestMatchDict(object):
    '''Nearest match based on key.

    Example:
    >>> bmd = BestMatchDict([('b', 'batman'), ('x', 'x-men')], default='aquaman')
    >>> bmd['a']
    'aquaman'
    >>> bmd['b']
    'batman'
    >>> bmd['w']
    'batman'
    >>> bmd['x']
    'x-men'
    >>> bmd['y']
    'x-men'
    '''
    def __init__(self, items, default=None):
        self._items = sorted(items, key=operator.itemgetter(0))
        self._keys = [key for (key, value) in self._items]
        self.default = default

    def __iter__(self):
        return iter(self._keys)

    def keys(self):
        return self._keys

    def __getitem__(self, key):
        i = bisect.bisect(self._keys, key)
        if i == 0:
            if self.default is None:
                raise KeyError
            return self.default

        # i points at match + 1
        return self._items[i - 1][1]
