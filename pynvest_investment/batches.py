import django
import urllib2
import pynvest_connect
from . import models

import os


def _populate_prices(investment, fix_existing, historicalprices):
    dirty_dates = set()
    for row in pynvest_connect.historical_prices(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
        historicalprice = historicalprices.setdefault(row.date, models.HistoricalPrice(investment=investment, date=row.date))
        if (historicalprice.high  == row.high and
            historicalprice.low   == row.low and
            historicalprice.close == row.close):
            if fix_existing:
                continue
            else:
                break

        historicalprice.high = row.high
        historicalprice.low = row.low
        historicalprice.close = row.close
        historicalprice.save()
        dirty_dates.add(row.date)
    return dirty_dates

def _populate_dividends(investment, fix_existing, historicalprices):
    dividends = dict((dividend.investment.date, dividend)
                         for dividend in models.Dividend.objects.select_related()
                                                                .filter(historicalprice__investment=investment))
    dirty_dates = set()
    for row in pynvest_connect.dividends(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
        dividend = dividends.setdefault(row.date, models.Dividend(historicalprice=historicalprices[row.date]))
        if dividend.amount == row.amount:
            if fix_existing:
                continue
            else:
                break

        dividend.amount = row.amount
        dividend.save()
        dirty_dates.add(row.date)
    return dirty_dates

def _populate_splits(investment, fix_existing, historicalprices):
    splits = dict((split.date, split)
                      for split in models.Split.objects.select_related()
                                                       .filter(historicalprice__investment=investment))
    dirty_dates = set()
    for row in pynvest_connect.splits(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
        split = splits.setdefault(row.date, models.Split(historicalprice=historicalprices[row.date]))
        if split.before == row.before and split.after == row.after:
            if fix_existing:
                continue
            else:
                break

        split.before = row.before
        split.after = row.after
        split.save()
        dirty_dates.add(row.date)
    return dirty_dates


def populate(*investments, **kwargs):
    fix_existing = kwargs.pop('fix_existing', False)
    output = kwargs.pop('output', open(os.devnull, 'w'))
    investments = investments or models.Investment.objects.all()

    num_investments = len(investments)
    for (index, investment) in enumerate(investments):
        if isinstance(investment, basestring):
            investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

        output.write('%3d/%d %-11s ' % (index + 1, num_investments, investment.symbol))

        dirty_dates = set()
        with django.db.transaction.commit_on_success():
            historicalprices = dict((historicalprice.date, historicalprice) for historicalprice in investment.historicalprice_set.all())
            for func in [_populate_prices, _populate_dividends, _populate_splits]:
                try:
                    dirty_dates.update(func(investment, fix_existing, historicalprices))
                except pynvest_connect.CallNotSupportedException:
                    pass

        if dirty_dates:
            if len(dirty_dates) > 1:
                output.write(min(dirty_dates).strftime('%Y-%m-%d - '))
            output.write(max(dirty_dates).strftime('%Y-%m-%d'))

        output.write('\n')
