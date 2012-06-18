import urllib2
import csv
import datetime
import decimal


def _convert(field):
    if '-' in field:
        return datetime.date(*map(int, field.split('-')))
    else:
        return decimal.Decimal(field)


def historic_prices(symbol):
    response = urllib2.urlopen('http://ichart.finance.yahoo.com/table.csv?s=%s' % symbol)
    try:
        raw = csv.reader(response)

        directives = map(str.lower, next(raw))
        return [dict(zip(directives, map(_convert, row))) for row in raw]
    finally:
        response.close()
