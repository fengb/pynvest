import urllib2
import collections
import csv
import datetime
import decimal


SUPPORTED_JURISDICTIONS = set(['CASH'])


_PRICES_TUPLE = collections.namedtuple('HistoricalPrice', 'date high low close')
_PRICES = _PRICES_TUPLE(datetime.date(1900, 1, 1), decimal.Decimal(1), decimal.Decimal(1), decimal.Decimal(1))
def historical_prices(*args, **kwargs):
    return [_PRICES]


def dividends(*args, **kwargs):
    return []


def splits(*args, **kwargs):
    return []
