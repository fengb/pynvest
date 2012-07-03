from django.db import models, transaction
import pynvest_connect
import datetime


def yesterday():
    return datetime.date.today() - datetime.timedelta(1)


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
        return self.historicalprice_set.latest('date').close

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
    def populate(cls, investment):
        if isinstance(investment, basestring):
            investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

        prices = pynvest_connect.historical_prices(investment.symbol)

        try:
            self = cls.objects.get(investment=investment)
        except cls.DoesNotExist:
            self = cls(investment=investment)

        self.start_date = min(prices[-1].date, self.start_date or prices[-1].date)
        self.end_date = max(prices[0].date, yesterday())
        self.save()

        self.populate_prices(prices)

    def populate_prices(self, prices):
        '''Short circuits upon first duplicate entry.'''
        for row in prices:
            if self.investment.historicalprice_set.filter(date=row.date).exists():
                break

            price = HistoricalPrice.objects.create(
                investment=self.investment,
                date=row.date,
                high=row.high,
                low=row.low,
                close=row.close,
            )
