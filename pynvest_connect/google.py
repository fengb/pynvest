import urllib2
import collections
import csv
import re
import datetime
import decimal


def convert_string(string):
    if '-' in string:
        return datetime.datetime.strptime(string, '%d-%b-%y').date()
    else:
        return decimal.Decimal(string)


_DIRECTIVES_PATTERN = re.compile('[\W_]+')
def adjusted_historical_prices(symbol, start_date=None, end_date=None):
    params = ['q=%s' % symbol, 'output=csv']
    if start_date:
        params.append(start_date.strftime('startdate=%b+%d,+%Y'))
    if end_date:
        params.append(end_date.strftime('enddate=%b+%d,+%Y'))

    response = urllib2.urlopen('http://www.google.com/finance/historical?' + '&'.join(params))
    try:
        raw = csv.reader(response)

        tuple = collections.namedtuple('HistoricalPrice', [_DIRECTIVES_PATTERN.sub('', directive.lower()) for directive in next(raw)])
        return [tuple(*map(convert_string, row)) for row in raw]
    finally:
        response.close()
