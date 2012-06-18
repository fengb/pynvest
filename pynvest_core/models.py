from django.db import models
import pynvest_connect


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

    def price_at(self, date):
        HistoricalPriceMeta.populate(self, date)
        self.historicalprice_set.get(date=date)


class HistoricalPrice(models.Model):
    investment      = models.ForeignKey(Investment)
    date            = models.DateField()
    high            = models.DecimalField(max_digits=12, decimal_places=4)
    low             = models.DecimalField(max_digits=12, decimal_places=4)
    close           = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.date, self.close)


def get_or_new(relation, *args, **kwargs):
    try:
        return relation.get(*args, **kwargs)
    except relation.model.DoesNotExist:
        return relation.model(*args, **kwargs)

class HistoricalPriceMeta(models.Model):
    investment      = models.OneToOneField(Investment)
    start_date      = models.DateField()
    end_date        = models.DateField()

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.start_date, self.end_date)

    @classmethod
    def populate(cls, investment, target_date):
        try:
            self = cls.objects.get(investment=investment)
        except cls.DoesNotExist:
            self = cls(investment=investment)

        if self.start_date is None or self.end_date is None or \
           self.start_date > target_date or self.end_date < target_date:
            prices = pynvest_connect.historical_prices(investment.symbol)
            self.start_date = prices[-1]['date']
            self.end_date = prices[0]['date']
            self.save()
            for row in prices:
                price = investment.historicalprice_set.get_or_create(date=row['date'], defaults={
                    'high': 0.0,
                    'low': 0.0,
                    'close': 0.0,
                })
                price.high = row['high']
                price.low = row['low']
                price.close = row['close']
                price.save()
