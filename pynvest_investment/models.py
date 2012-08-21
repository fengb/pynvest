from django.db import models, transaction
import django
import pynvest_connect
import datetime
import urllib2

from . import managers

@django.dispatch.receiver(django.db.backends.signals.connection_created)
def add_sqlite_math_functions(connection, **kwargs):
    if connection.vendor != 'sqlite':
        return

    class Product:
        def __init__(self):
            self.product = 1

        def step(self, value):
            self.product *= value

        def finalize(self):
            return self.product

    connection.connection.create_aggregate('product', 1, Product)


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

    def latest_snapshot(self):
        return self.snapshot_set.latest('date')

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

    objects = managers.QuerySetManager()
    class QuerySet(models.query.QuerySet):
        def filter_year_range(self, end_date=None):
            end_date = end_date or datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)
            return self.filter(date__lte=end_date, date__gte=start_date)

        def close_adjusted(self):
            func = 'PRODUCT(close / (close + dividend))'
            subquery = '''SELECT %(table)s.close * COALESCE(%(func)s, 1)
                            FROM %(table)s t
                           WHERE investment_id = %(table)s.investment_id
                             AND dividend > 0
                             AND date > %(table)s.date
                       ''' % {'table': self.model._meta.db_table, 'func': func}
            return self.extra(select={'close_adjusted': subquery})

    @classmethod
    @transaction.commit_on_success
    def batch_populate(cls, fix_existing=False):
        investments = Investment.objects.all()

        for investment in investments:
            if isinstance(investment, basestring):
                investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

            try:
                existing_snapshots = dict((snapshot.date, snapshot) for snapshot in investment.snapshot_set.all())
                prices = pynvest_connect.historical_prices(investment.symbol)
                for row in prices:
                    if row.date in existing_snapshots:
                        snapshot = existing_snapshots[row.date]
                        if (snapshot.high  != row.high or
                            snapshot.low   != row.low or
                            snapshot.close != row.close):
                            snapshot.high = row.high
                            snapshot.low = row.low
                            snapshot.close = row.close
                            snapshot.save()
                        elif not fix_existing:
                            # Assume the rest are duplicate entries
                            break
                    else:
                        snapshot = Snapshot.objects.create(
                            investment=investment,
                            date=row.date,
                            high=row.high,
                            low=row.low,
                            close=row.close,
                        )

                dividends = pynvest_connect.dividends(investment.symbol)
                for dividend in dividends:
                    snapshot = investment.snapshot_set.get(date=dividend.date)
                    if snapshot.dividend:
                          break

                    snapshot.dividend = dividend.amount
                    snapshot.save()

                splits = pynvest_connect.splits(investment.symbol)
                for split in splits:
                    snapshot = investment.snapshot_set.get(date=split.date)
                    if not (snapshot.split_before == 1 and snapshot.split_after == 1):
                          break

                    snapshot.split_before = split.before
                    snapshot.split_after = split.after
                    snapshot.save()
            except urllib2.HTTPError, e:
                if e.code != 404:
                    raise
                else:
                    # Not found but continue anyway
                    pass
