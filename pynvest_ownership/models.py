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

    @classmethod
    def amount_at(cls, portfolio, date):
        return pynvest_portfolio.presenters.PortfolioGrowth(portfolio)[date]

    @classmethod
    def units_for_new_amount(cls, portfolio, date, amount):
        return amount * cls.total_units(portfolio, date) / \
               (cls.amount_at(portfolio, date) - amount)

    @classmethod
    def new(cls, user, portfolio, date, amount):
        return cls(user=user, portfolio=portfolio, date=date,
                   units=cls.units_for_new_amount(portfolio, date, amount))

    def amount(self):
        percentage = self.units / self.total_units(self.portfolio, self.date)
        return percentage * self.amount_at(self.portfolio, self.date)
