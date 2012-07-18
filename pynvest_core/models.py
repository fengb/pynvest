from django.db import models, transaction
import pynvest_connect.yahoo
import datetime
import urllib2


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


class Snapshot(models.Model):
    investment      = models.ForeignKey(Investment)
    date            = models.DateField()
    high            = models.DecimalField(max_digits=12, decimal_places=4)
    low             = models.DecimalField(max_digits=12, decimal_places=4)
    close           = models.DecimalField(max_digits=12, decimal_places=4)
    dividend        = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.date, self.close)


    @classmethod
    @transaction.commit_on_success
    def batch_populate(cls, *investments):
        if not investments:
            investments = Investment.objects.all()

        for investment in investments:
            try:
                if isinstance(investment, basestring):
                    investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

                populated_dates = set(investment.snapshot_set.values_list('date', flat=True))
                prices = pynvest_connect.yahoo.historical_prices(investment.symbol)
                for row in prices:
                    if row.date in populated_dates:
                        break

                    snapshot = Snapshot.objects.create(
                        investment=investment,
                        date=row.date,
                        high=row.high,
                        low=row.low,
                        close=row.close,
                    )

                dividends = pynvest_connect.yahoo.dividends(investment.symbol)
                for dividend in dividends:
                    snapshot = investment.snapshot_set.get(date=dividend.date)
                    if snapshot.dividend:
                          break

                    snapshot.dividend = dividend.amount
                    snapshot.save()
            except urllib2.HTTPError, e:
                if e.code != 404:
                    raise
