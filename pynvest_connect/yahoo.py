import urllib2
import collections
import csv
import datetime
import decimal


def _convert(field):
    if '-' in field:
        return datetime.date(*map(int, field.split('-')))
    else:
        return decimal.Decimal(field)


def historical_prices(symbol, start_date=None, end_date=None):
    # Yahoo API is really terrible... abcdef go!
    params = ['s=%s' % symbol]
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

    response = urllib2.urlopen('http://ichart.finance.yahoo.com/table.csv?' + '&'.join(params))
    try:
        raw = csv.reader(response)

        tuple = collections.namedtuple('RawPrice', [directive.lower().replace(' ', '_') for directive in next(raw)])
        return [tuple(*map(_convert, row)) for row in raw]
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
        return _FIELDS_TUPLE(*map(_convert, next(raw)))
    finally:
        response.close()
