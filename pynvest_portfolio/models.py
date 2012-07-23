from django.db import models
import pynvest_core
from . import managers


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class Lot(models.Model):
    investment      = models.ForeignKey(pynvest_core.models.Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    def base_transaction(self):
        return self.transaction_set.order_by('date')[0]

    def purchase_date(self):
        return self.base_transaction().date

    def purchase_price(self):
        return self.base_transaction().price

    def purchase_value(self):
        return self.purchase_price() * self.outstanding_shares

    def current_price(self):
        return self.investment.current_price()

    def current_value(self):
        return self.current_price() * self.outstanding_shares

    def unrealized_gain(self):
        return (self.current_price() - self.purchase_price()) * self.outstanding_shares

    def unrealized_gain_percent(self):
        return self.unrealized_gain() / self.purchase_value() * 100

    objects = managers.AnnotatedLotManager()


class Transaction(models.Model):
    lot             = models.ForeignKey(Lot)
    date            = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.date, self.value())

    @property
    def investment(self):
        return self.lot.investment

    def base_transaction(self):
        return self.lot.base_transaction()

    def value(self):
        return self.price * self.shares

    def realized_gain(self):
        return -self.shares * (self.price - self.base_transaction().price)
