from django.db import models
from django.contrib import admin


class Investment(models.Model):
    symbol          = models.CharField(max_length=5, unique=True)
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.symbol

    class Admin(object): pass


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name

    class Admin(object): pass


class Basis(models.Model):
    investment      = models.ForeignKey(Investment)
    portfolio       = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    class Admin(object): pass


class Transaction(models.Model):
    basis           = models.ForeignKey(Basis)
    date            = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)
    shares          = models.DecimalField(max_digits=15, decimal_places=4)

    def __unicode__(self):
        return u'%s %s' % (self.basis, self.date)

    def total(self):
        return price * shares

    class Admin(object): pass


for obj in locals().values():
    if 'Admin' in dir(obj):
        admin.site.register(obj)
