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


class Basis(models.Model):
    investment      = models.ForeignKey(Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    def created_date(self):
        return min(transaction.date
                     for transaction in self.transaction_set.all())

    def updated_date(self):
        return max(transaction.date
                     for transaction in self.transaction_set.all())

    def shares(self):
        return sum(transaction.shares
                     for transaction in self.transaction_set.all())


class Transaction(models.Model):
    basis           = models.ForeignKey(Basis)
    date            = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    def __unicode__(self):
        return u'%s %s' % (self.basis, self.date)

    def total(self):
        return price * shares
