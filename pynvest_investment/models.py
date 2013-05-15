from django.db import models
import django.db.backends.signals
import datetime
import decimal

from . import managers


class Jurisdiction(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name   = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.symbol


class Investment(models.Model):
    jurisdiction = models.ForeignKey(Jurisdiction)
    symbol       = models.CharField(max_length=10, unique=True)
    name         = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % (self.symbol)

    def current_price(self):
        return self.historicalprice_set.latest('date').close

    def _year_data(self, field):
        if not hasattr(self, '_year_data_cache'):
            self._year_data_cache = self.historicalprice_set.filter_year_range().aggregate(high=models.Max('high'), low=models.Min('low'))
        return self._year_data_cache[field]

    def year_high(self):
        return self._year_data('high')

    def year_low(self):
        return self._year_data('low')

    @property
    def snapshot_set(self):
        return self.historicalprice_set.snapshot()


class HistoricalPrice(models.Model):
    investment = models.ForeignKey(Investment)
    date       = models.DateField(db_index=True)
    high       = models.DecimalField(max_digits=12, decimal_places=4)
    low        = models.DecimalField(max_digits=12, decimal_places=4)
    close      = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        unique_together = [('investment', 'date')]

    def adjusted(self, field):
        return getattr(self, field) * decimal.Decimal(self.price_adjustment)

    def close_adjusted(self):
        return self.adjusted('close')

    objects = managers.QuerySetManager()
    class QuerySet(models.query.QuerySet):
        def snapshot(self):
            return self.select_related('dividend', 'split').extra(select={'price_adjustment': '''
                SELECT pa.raw / pa_latest.raw
                  FROM %(priceadjustment)s pa
                 INNER JOIN (SELECT *
                               FROM %(priceadjustment)s pa
                              INNER JOIN %(self)s hp
                                      ON hp.id = pa.historicalprice_id
                              WHERE hp.investment_id = %(self)s.investment_id
                              ORDER BY hp.date DESC
                              LIMIT 1
                            ) pa_latest
                         ON 1 = 1
                 WHERE pa.historicalprice_id = %(self)s.id
            '''% {'self': self.model._meta.db_table, 'priceadjustment': PriceAdjustment._meta.db_table}})

        def filter_year_range(self, end_date=None):
            end_date = end_date or datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)
            return self.filter(date__lte=end_date, date__gte=start_date)


class Dividend(models.Model):
    historicalprice = models.OneToOneField(HistoricalPrice)
    amount          = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return '%s' % amount

    def percent(self):
        return self.amount / self.historicalprice.close


class Split(models.Model):
    historicalprice = models.OneToOneField(HistoricalPrice)
    before          = models.IntegerField()
    after           = models.IntegerField()

    def __unicode__(self):
        return '%d:%d' % (self.after, self.before)


class PriceAdjustment(models.Model):
    historicalprice = models.OneToOneField(HistoricalPrice)
    # Store as Float since it accomodates sigfigs better than Decimal
    # Sigfigs are more important than digit accuracy for multiplication
    raw             = models.FloatField()

    def __unicode__(self):
        return '%s %s' % (self.historicalprice, self.raw)
