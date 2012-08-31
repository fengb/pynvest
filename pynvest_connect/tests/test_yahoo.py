import pytest
import datetime

import pynvest_connect.yahoo


class TestHistoricalPrices(object):
    def test_single_date(self):
        prices = pynvest_connect.yahoo.historical_prices('KO', start_date=datetime.date(2012, 3, 12), end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 1
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[0].close * 100 == 7015

    def test_multiple_dates_in_reverse_order(self):
        prices = pynvest_connect.yahoo.historical_prices('KO', start_date=datetime.date(2012, 3, 12), end_date=datetime.date(2012, 3, 14))

        assert len(prices) == 3
        assert prices[0].date == datetime.date(2012, 3, 14)
        assert prices[1].date == datetime.date(2012, 3, 13)
        assert prices[2].date == datetime.date(2012, 3, 12)

    def test_ignore_missing_dates(self):
        prices = pynvest_connect.yahoo.historical_prices('KO', start_date=datetime.date(2012, 3, 9), end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 2
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[1].date == datetime.date(2012, 3, 9)

    def test_funny_symbols(self):
        prices = pynvest_connect.yahoo.historical_prices('BRK.B', start_date=datetime.date(2012, 3, 12), end_date=datetime.date(2012, 3, 12))

        assert len(prices) == 1
        assert prices[0].date == datetime.date(2012, 3, 12)
        assert prices[0].close * 100 == 7954


class TestDividends(object):
    @pytest.mark.xfail
    # Yahoo has adjusted dividends
    def test_single_dividend(self):
        dividends = pynvest_connect.yahoo.dividends('KO', start_date=datetime.date(2012, 3, 13), end_date=datetime.date(2012, 3, 13))

        assert len(dividends) == 1
        assert dividends[0].amount * 100 == 51

    def test_multiple_dividends_in_reverse_order(self):
        dividends = pynvest_connect.yahoo.dividends('KO', start_date=datetime.date(2012, 3, 13), end_date=datetime.date(2012, 6, 13))

        assert len(dividends) == 2
        assert dividends[0].date == datetime.date(2012, 6, 13)
        assert dividends[1].date == datetime.date(2012, 3, 13)
