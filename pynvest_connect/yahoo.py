import urllib2
import collections
import csv
import datetime
import decimal


def convert_string(field, strptime_string=None, strptime_cache={}):
    if '-' in field:
        return datetime.date(*map(int, field.split('-')))
    else:
        return decimal.Decimal(field)


def _ichart_request(symbol, start_date, end_date, extra_params=[], resource='table.csv'):
    params = ['s=' + symbol]
    params.extend(extra_params)
    # Yahoo API is really terrible... abcdef go!
    if start_date:
        params.extend([
            # POSIX date means January=0, February=1, etc.
            'a=%d' % (start_date.month - 1),
            'b=%d' % (start_date.day),
            'c=%d' % (start_date.year),
        ])
    if end_date:
        params.extend([
            'd=%d' % (end_date.month - 1),
            'e=%d' % (end_date.day),
            'f=%d' % (end_date.year),
        ])
    return urllib2.urlopen('http://ichart.finance.yahoo.com/%s?%s' % (resource, '&'.join(params)))


def historical_prices(symbol, start_date=None, end_date=None):
    response = _ichart_request(symbol, start_date, end_date)
    try:
        raw = csv.reader(response)

        tuple = collections.namedtuple('HistoricalPrice', [directive.lower().replace(' ', '_') for directive in next(raw)])
        return [tuple(*map(convert_string, row)) for row in raw]
    finally:
        response.close()


_DIVIDENDS_TUPLE = collections.namedtuple('Dividend', 'date amount')
def dividends(symbol, start_date=None, end_date=None):
    response = _ichart_request(symbol, start_date, end_date, extra_params=['g=v'])
    try:
        raw = csv.reader(response)

        next(raw) # remove directives row
        return [_DIVIDENDS_TUPLE(*map(convert_string, row)) for row in raw]
    finally:
        response.close()


_FIELDS = {
    'l1': 'price',
    'r0': 'pe_ratio',
}
_FIELDS_REMOTE = _FIELDS.keys()
_FIELDS_TUPLE = collections.namedtuple('CurrentValues', _FIELDS.values())
def current_values(symbol):
    params = ['s=%s' % symbol, 'f=%s' % ''.join(_FIELDS_REMOTE)]

    response = urllib2.urlopen('http://finance.yahoo.com/d/quotes.csv?' + '&'.join(params))
    try:
        raw = csv.reader(response)
        return _FIELDS_TUPLE(*map(convert_string, next(raw)))
    finally:
        response.close()
