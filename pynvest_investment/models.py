from django.db import models, transaction
import django
import pynvest_connect
import datetime
import urllib2
import math

from . import managers

@django.dispatch.receiver(django.db.backends.signals.connection_created)
def add_sqlite_math_functions(connection, **kwargs):
    connection.connection.create_function('ln', 1, math.log)
    connection.connection.create_function('exp', 1, math.exp)


class Exchange(models.Model):
    symbol          = models.CharField(max_length=10, unique=True)
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.symbol


class Investment(models.Model):
    exchange        = models.ForeignKey(Exchange)
    symbol          = models.CharField(max_length=10, unique=True)
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % (self.symbol)

    def current_price(self):
        return self.snapshot_set.latest('date').close

    def _year_data(self, field):
        if not hasattr(self, '_year_data_cache'):
            self._year_data_cache = self.snapshot_set.filter_year_range().aggregate(high=models.Max('high'), low=models.Min('low'))
        return self._year_data_cache[field]

    def year_high(self):
        return self._year_data('high')

    def year_low(self):
        return self._year_data('low')


class Snapshot(models.Model):
    investment      = models.ForeignKey(Investment)
    date            = models.DateField(db_index=True)
    high            = models.DecimalField(max_digits=12, decimal_places=4)
    low             = models.DecimalField(max_digits=12, decimal_places=4)
    close           = models.DecimalField(max_digits=12, decimal_places=4)
    dividend        = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    split_before    = models.IntegerField(default=1)
    split_after     = models.IntegerField(default=1)

    class Meta:
        unique_together = [('investment', 'date')]

    def dividend_percent(self):
        return self.dividend / self.close

    def split(self):
        if self.split_before == 1 and self.split_after == 1:
            return ''

        return '%d:%d' % (self.split_after, self.split_before)

    objects = managers.QuerySetManager()
    class QuerySet(models.query.QuerySet):
        def filter_year_range(self, end_date=None):
            end_date = end_date or datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)
            return self.filter(date__lte=end_date, date__gte=start_date)

        def close_adjusted(self):
            aggr_func = 'SUM(LN(1.0 * close / (close + dividend) * split_before / split_after))'
            subquery = '''SELECT %(table)s.close * EXP(COALESCE(%(aggr_func)s, 0))
                            FROM %(table)s t
                           WHERE investment_id = %(table)s.investment_id
                             AND (dividend > 0 OR split_before != 1 OR split_after != 1)
                             AND date > %(table)s.date
                       ''' % {'table': self.model._meta.db_table, 'aggr_func': aggr_func}
            return self.extra(select={'close_adjusted': subquery})

    @classmethod
    @transaction.commit_on_success
    def batch_populate(cls, *investments, **kwargs):
        fix_existing = kwargs.pop('fix_existing', False)
        investments = investments or Investment.objects.all()

        for investment in investments:
            if isinstance(investment, basestring):
                investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

            try:
                all_snapshots = dict((snapshot.date, snapshot) for snapshot in investment.snapshot_set.all())
                prices = pynvest_connect.historical_prices(investment.symbol)
                dirty_snapshots = set()
                for row in prices:
                    snapshot = all_snapshots.setdefault(row.date, Snapshot(investment=investment, date=row.date))
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
                    dirty_snapshots.add(snapshot)

                dividends = pynvest_connect.dividends(investment.symbol)
                for dividend in dividends:
                    snapshot = all_snapshots[dividend.date]
                    if snapshot.dividend == dividend.amount:
                        if fix_existing:
                            continue
                        else:
                            break

                    snapshot.dividend = dividend.amount
                    dirty_snapshots.add(snapshot)

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
                    dirty_snapshots.add(snapshot)
                for snapshot in dirty_snapshots:
                    snapshot.save()
            except urllib2.HTTPError, e:
                if e.code != 404:
                    raise
                else:
                    # Not found but continue anyway
                    pass
