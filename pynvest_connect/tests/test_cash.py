import datetime

import pynvest_connect


def pytest_generate_tests(metafunc):
    testfunc = metafunc.cls.func
    supported = [m for m in pynvest_connect._MODULES if hasattr(m, testfunc) and
                                                        'CASH' in m.SUPPORTED_JURISDICTIONS]
    metafunc.parametrize('module', supported)


class TestHistoricalPrices(object):
    func = 'historical_prices'

    def test_single_date(self, module):
        prices = module.historical_prices('USD')

        assert len(prices) == 1
        assert prices[0].date == datetime.date(1900, 1, 1)
        assert prices[0].high == 1
        assert prices[0].low == 1
        assert prices[0].close == 1


class TestDividends(object):
    func = 'dividends'

    def test_never_any_dividends(self, module):
        dividends = module.dividends('USD')
        assert len(dividends) == 0


class TestSplits(object):
    func = 'splits'

    def test_never_any_splits(self, module):
        splits = module.splits('USD')
        assert len(splits) == 0
