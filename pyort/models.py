from django.db import models


class Investment(models.Model):
    symbol          = models.CharField(max_length=5, unique=True)
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.symbol


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name


class Lot(models.Model):
    investment      = models.ForeignKey(Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)


class Transaction(models.Model):
    lot             = models.ForeignKey(Lot)
    trade_date      = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    def __unicode__(self):
        return u'%s %s' % (self.lot, self.date)

    @property
    def investment(self):
        return self.lot.investment
