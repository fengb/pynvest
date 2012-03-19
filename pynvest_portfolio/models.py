from django.db import models
import pynvest_core


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class Transaction(models.Model):
    investment      = models.ForeignKey(pynvest_core.models.Investment)
    portfolio       = models.ForeignKey(Portfolio)
    trade_date      = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.trade_date, self.amount())

    @property
    def shares(self):
        return sum(lt.shares for lt in self.lottransaction_set.all())

    def amount(self):
        return self.price * self.shares


class Lot(models.Model):
    investment      = models.ForeignKey(pynvest_core.models.Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    def purchase_transaction(self):
        return self.lot_transaction_set.order_by('transaction__trade_date')[0]

    def shares(self):
        return sum(t.shares for t in self.transaction_set.all())


class LotTransaction(models.Model):
    lot             = models.ForeignKey(Lot)
    transaction     = models.ForeignKey(Transaction)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    @property
    def trade_date(self):
        return self.transaction.trade_date

    @property
    def price(self):
        return self.transaction.price
