from django.db import models, transaction
import pynvest_connect
import datetime


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

    def price_at(self, target_date):
        '''latest close price <= target_date
        Cannot do simple == target_date because weekends/holidays do not have prices

        Example:
        >>> i.price_at(datetime.date(2011,11,25))
        <close price of 2011-11-25>

        # Saturday
        >>> i.price_at(datetime.date(2011,11,26))
        <close price of 2011-11-25>

        # Thanksgiving
        >>> i.price_at(datetime.date(2011,11,24))
        <close price of 2011-11-23>
        '''
        HistoricalPriceMeta.populate(self, target_date)
        return self.historicalprice_set.filter(date__lte=target_date).latest('date').close


class HistoricalPrice(models.Model):
    investment      = models.ForeignKey(Investment)
    date            = models.DateField()
    high            = models.DecimalField(max_digits=12, decimal_places=4)
    low             = models.DecimalField(max_digits=12, decimal_places=4)
    close           = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.date, self.close)


class HistoricalPriceMeta(models.Model):
    investment      = models.OneToOneField(Investment)
    start_date      = models.DateField()
    end_date        = models.DateField()

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.start_date, self.end_date)

    @classmethod
    @transaction.commit_on_success
    def populate(cls, investment, target_date):
        yesterday = datetime.date.today() - datetime.timedelta(1)
        if target_date > yesterday:
            raise ValueError('target_date must be in the past: %s' % target_date)

        self, created = cls.objects.get_or_create(investment=investment, defaults={
            # Dummy values to force data load
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today(),
        })

        if self.start_date > target_date or self.end_date < target_date:
            prices = pynvest_connect.historical_prices(investment.symbol)

            self.start_date = prices[-1]['date']
            self.end_date = yesterday
            self.save()

            for row in prices:
                price, created = investment.historicalprice_set.get_or_create(date=row['date'], defaults={
                    'high': 0,
                    'low': 0,
                    'close': 0,
                })
                price.high = row['high']
                price.low = row['low']
                price.close = row['close']
                price.save()
