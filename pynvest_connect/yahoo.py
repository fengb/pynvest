import urllib2
import collections
import csv
import datetime
import decimal


SUPPORTED_JURISDICTIONS = set(['SEC'])


def convert_string(field, strptime_string=None, strptime_cache={}):
    if '-' in field:
        return datetime.date(*map(int, field.split('-')))
    else:
        return decimal.Decimal(field)


def _ichart_request(symbol, start_date, end_date=None, extra_params=[], resource='table.csv'):
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
_SPLITS_TUPLE = collections.namedtuple('Split', 'date before after')
def _splits_dividends(symbol, start_date=None, end_date=None):
    # Yahoo dividends are split adjusted so we have to unadjust them manually
    end_date = end_date or datetime.date.today()

    # What the hell is 'x'?  I really hate Yahoo API...
    response = _ichart_request(symbol, start_date, extra_params=['g=v'], resource='x')
    try:
        raw = csv.reader(response)

        next(raw) # remove directives row. Useless AND wrong this time!
        splits = []
        dividends = []
        before_adjust = decimal.Decimal(1)
        after_adjust = decimal.Decimal(1)
        for row in raw:
            if row[0].lower() == 'split':
                type, date, value = row
                # Can't use convert_string because date is in a different format...
                date = datetime.datetime.strptime(date.strip(), '%Y%m%d').date()

                # Split 2:1 means 1 share turns into 2
                after, before = map(int, value.split(':'))
                before_adjust *= before
                after_adjust *= after
                if date <= end_date:
                    splits.append(_SPLITS_TUPLE(date, before, after))
            elif row[0].lower() == 'dividend':
                type, date, value = row
                # Can't use convert_string because date is in a different format...
                date = datetime.datetime.strptime(date.strip(), '%Y%m%d').date()

                if date <= end_date:
                    dividends.append(_DIVIDENDS_TUPLE(date, decimal.Decimal(value) * after_adjust / before_adjust))
        return splits, dividends
    finally:
        response.close()


def dividends(*args, **kwargs):
    return _splits_dividends(*args, **kwargs)[1]


def splits(*args, **kwargs):
    return _splits_dividends(*args, **kwargs)[0]


def adjusted_dividends(symbol, start_date=None, end_date=None):
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
