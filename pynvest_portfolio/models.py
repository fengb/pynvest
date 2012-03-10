from django.db import models
import pynvest_core


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class Lot(models.Model):
    investment      = models.ForeignKey(pynvest_core.models.Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    def purchase_transaction(self):
        return self.transaction_set.order_by('trade_date')[0]

    def gains(self):
        return -sum(t.amount() for t in self.transaction_set.all()) + self.shares() * self.purchase_transaction().price

    def shares(self):
        return sum(t.shares for t in self.transaction_set.all())


class Transaction(models.Model):
    lot             = models.ForeignKey(Lot)
    trade_date      = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.trade_date, self.amount())

    @property
    def investment(self):
        return self.lot.investment

    def amount(self):
        return self.price * self.shares
