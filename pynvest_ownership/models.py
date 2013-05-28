from django.db import models
from django.contrib import auth

import pynvest_portfolio


class Contribution(models.Model):
    user        = models.ForeignKey(auth.models.User)
    transaction = models.OneToOneField(pynvest_portfolio.models.Transaction)

    def __unicode__(self):
        return u'%s %s %s' % (self.user, self.transaction.date, self.transaction.value())


class UnitContribution(models.Model):
    contribution = models.OneToOneField(Contribution)
    units        = models.DecimalField(max_digits=18, decimal_places=8)

    def __unicode__(self):
        return u'%s %s' % (self.contribution, self.units)
