from pynvest_investment import utils
import pytest


class TestBestMatchDict(object):
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

        def test_missing_key_smaller_than_all_keys_generates_exception(self):
            with pytest.raises(KeyError):
                self.d[0]
