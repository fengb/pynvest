import datetime

import pynvest_connect


def pytest_generate_tests(metafunc):
    testfunc = metafunc.cls.func
    supported = [m for m in pynvest_connect._MODULES if hasattr(m, testfunc) and
                                                        'SEC' in m.SUPPORTED_JURISDICTIONS]
    metafunc.parametrize('module', supported)


class TestHistoricalPrices(object):
    func = 'historical_prices'

    def test_single_date(self, module):
        prices = module.historical_prices('KO', start_date=datetime.date(2012, 3, 12),
                                                end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 1
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[0].close * 100 == 7015

    def test_multiple_dates_in_reverse_order(self, module):
        prices = module.historical_prices('KO', start_date=datetime.date(2012, 3, 12),
                                                end_date=datetime.date(2012, 3, 14))

        assert len(prices) == 3
        assert prices[0].date == datetime.date(2012, 3, 14)
        assert prices[1].date == datetime.date(2012, 3, 13)
        assert prices[2].date == datetime.date(2012, 3, 12)

    def test_ignore_missing_dates(self, module):
        prices = module.historical_prices('KO', start_date=datetime.date(2012, 3, 9),
                                                end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 2
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[1].date == datetime.date(2012, 3, 9)

    def test_funny_symbols(self, module):
        prices = module.historical_prices('BRK.B', start_date=datetime.date(2012, 3, 12),
                                                   end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 1
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[0].close * 100 == 7954


class TestDividends(object):
    func = 'dividends'

    def test_single_dividend(self, module):
        dividends = module.dividends('KO', start_date=datetime.date(2012, 3, 13),
                                           end_date=datetime.date(2012, 3, 13))

        assert len(dividends) == 1
        assert dividends[0].amount * 100 == 51

    def test_multiple_dividends_in_reverse_order(self, module):
        dividends = module.dividends('KO', start_date=datetime.date(2012, 3, 13),
                                           end_date=datetime.date(2012, 6, 13))

        assert len(dividends) == 2
        assert dividends[0].date == datetime.date(2012, 6, 13)
        assert dividends[1].date == datetime.date(2012, 3, 13)


class TestAdjustedDividends(object):
    func = 'adjusted_dividends'

    def test_single_dividend(self, module):
        dividends = module.adjusted_dividends('KO', start_date=datetime.date(2012, 3, 13),
                                                    end_date=datetime.date(2012, 3, 13))

        assert len(dividends) == 1
        assert dividends[0].amount * 100 == 25.5

    def test_multiple_dividends_in_reverse_order(self, module):
        dividends = module.adjusted_dividends('KO', start_date=datetime.date(2012, 3, 13),
                                                    end_date=datetime.date(2012, 6, 13))

        assert len(dividends) == 2
        assert dividends[0].date == datetime.date(2012, 6, 13)
        assert dividends[1].date == datetime.date(2012, 3, 13)


class TestSplits(object):
    func = 'splits'

    def test_single_split(self, module):
        splits = module.splits('KO', start_date=datetime.date(2012, 8, 13),
                                     end_date=datetime.date(2012, 8, 13))

        assert len(splits) == 1
        assert splits[0].before == 1
        assert splits[0].after == 2

    def test_multiple_splits_in_reverse_order(self, module):
        splits = module.splits('KO', start_date=datetime.date(1996, 5, 13),
                                     end_date=datetime.date(2012, 8, 13))

        assert len(splits) == 2
        assert splits[0].date == datetime.date(2012, 8, 13)
        assert splits[1].date == datetime.date(1996, 5, 13)
