import urllib2
import collections
import csv
import re
import datetime
import decimal


def convert_string(string):
    if '/' in string:
        return datetime.datetime.strptime(string, '%M/%d/%Y')
    else:
        try:
            return decimal.Decimal(string.replace(',', ''))
        except decimal.InvalidOperation:
            return string


_DIRECTIVES_PATTERN = re.compile('[\W_]+')
def historical_prices(symbol, start_date=None, end_date=None):
    params = ['t=%s' % symbol, 'freq=d']
    if start_date:
        params.append('pd=custom')
        params.append(start_date.strftime('sd=%M/%d/%Y'))
        if end_date:
            params.append(start_date.strftime('startdate=%M/%d/%Y'))
    else:
        params.append('pd=max')

    response = urllib2.urlopen('http://performance.morningstar.com/Performance/stock/exportStockPrice.action?' + '&'.join(params))
    try:
        next(response)  # Worthless page header
        raw = csv.reader(response)

        tuple = collections.namedtuple('HistoricalPrice', [_DIRECTIVES_PATTERN.sub('', directive.lower()) for directive in next(raw)])
        return [tuple(*map(convert_string, row)) for row in raw]
    finally:
        response.close()
