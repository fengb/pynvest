import operator
import bisect


# FIXME: RENAME PLEASE
class BinarySearchThing(object):
    '''Nearest match based on key.

    Example:
    >>> bst = BinarySearchThing([('b', 'batman'), ('x', 'x-men')])
    >>> bst['b']
    'batman'
    >>> bst['w']
    'batman'
    >>> bst['x']
    'x-men'
    >>> bst['y']
    'x-men'
    '''
    def __init__(self, items):
        self._items = sorted(items, key=operator.itemgetter(0))
        self._keys = [key for (key, value) in self._items]

    def __iter__(self):
        return iter(self._keys)

    def keys(self):
        return self._keys

    def __getitem__(self, key):
        i = bisect.bisect(self._keys, key)

        # i points at match + 1
        return self._items[i - 1][1]
