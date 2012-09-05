from pynvest_investment import utils
import pytest


class TestBestMatchDict(object):
    class TestConstructor(object):
        def setup(self):
            # Assumed base case for comparison
            self.base = utils.BestMatchDict([('a', 'b'), ('c', 'd')])

        def test_out_of_order(self):
            d = utils.BestMatchDict([('a', 'b'), ('c', 'd')])
            assert d == self.base

        def test_dict(self):
            d = utils.BestMatchDict({'a': 'b', 'c': 'd'})

        def test_self(self):
            d = utils.BestMatchDict(self.base)
            assert d == self.base

    class TestGet(object):
        def setup(self):
            self.d = utils.BestMatchDict([(1, 'first'), (3, 'third')])

        def test_exact_key(self):
            assert self.d[1] == 'first'
            assert self.d[3] == 'third'

        def test_missing_key_as_nearest_match_rounded_down(self):
            assert self.d[2] == 'first'
            assert self.d[4] == 'third'
            assert self.d[100000] == 'third'

        def test_missing_key_smaller_than_all_keys_generates_exception_when_no_default(self):
            with pytest.raises(KeyError):
                self.d[0]

        def test_missing_key_smaller_than_all_keys_returns_default(self):
            self.d = utils.BestMatchDict([(1, 'first'), (3, 'third')], default='zero')
            assert self.d[0] == 'zero'
