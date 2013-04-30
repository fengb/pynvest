from django.db import models
from django.contrib import auth

import pynvest_portfolio
import pynvest_portfolio.presenters


class Contribution(models.Model):
    user      = models.ForeignKey(auth.models.User)
    portfolio = models.ForeignKey(pynvest_portfolio.models.Portfolio)
    date      = models.DateField()
    units     = models.DecimalField(max_digits=18, decimal_places=8)

    def __unicode__(self):
        return u'%s %s' % (self.user, self.units)

    @classmethod
    def total_units(cls, portfolio, date):
        return sum(Contribution.objects.filter(portfolio=portfolio, date__lte=date).values_list('units', flat=True))

    def amount(self):
        growth = pynvest_portfolio.presenters.PortfolioGrowth(self.portfolio)
        percentage = self.units / self.total_units(self.portfolio, self.date)
        return percentage * growth[self.date]
