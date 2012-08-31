import django
import urllib2
import pynvest_connect
from . import models

import sys


@django.db.transaction.commit_on_success
def populate(*investments, **kwargs):
    fix_existing = kwargs.pop('fix_existing', False)
    investments = investments or models.Investment.objects.all()

    for investment in investments:
        if isinstance(investment, basestring):
            investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

        try:
            all_snapshots = dict((snapshot.date, snapshot) for snapshot in investment.snapshot_set.all())
            prices = pynvest_connect.historical_prices(investment.symbol)
            dirty_dates = set()
            for row in prices:
                snapshot = all_snapshots.setdefault(row.date, models.Snapshot(investment=investment, date=row.date))
                if (snapshot.high  == row.high and
                    snapshot.low   == row.low and
                    snapshot.close == row.close):
                    if fix_existing:
                        continue
                    else:
                        break

                snapshot.high = row.high
                snapshot.low = row.low
                snapshot.close = row.close
                dirty_dates.add(snapshot.date)

            dividends = pynvest_connect.dividends(investment.symbol)
            for dividend in dividends:
                snapshot = all_snapshots[dividend.date]
                if snapshot.dividend == dividend.amount:
                    if fix_existing:
                        continue
                    else:
                        break

                snapshot.dividend = dividend.amount
                dirty_dates.add(snapshot.date)

            splits = pynvest_connect.splits(investment.symbol)
            for split in splits:
                snapshot = all_snapshots[split.date]
                if snapshot.split_before == split.before and snapshot.split_after == split.after:
                    if fix_existing:
                        continue
                    else:
                        break

                snapshot.split_before = split.before
                snapshot.split_after = split.after
                dirty_dates.add(snapshot.date)
            for date in dirty_dates:
                all_snapshots[date].save()
        except urllib2.HTTPError, e:
            if e.code != 404:
                raise
            else:
                # Not found but continue anyway
                pass
