import urllib2
import csv


def historical_prices(symbol):
    response = urllib2.urlopen('http://ichart.finance.yahoo.com/table.csv?s=%s' % symbol)
    try:
        raw = csv.reader(response)

        directives = map(str.lower, next(raw))
        return [dict(zip(directives, row)) for row in raw]
    finally:
        response.close()
