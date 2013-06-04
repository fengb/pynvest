from django.db import models
from django.contrib.auth.models import User

import pynvest_portfolio.models
import pynvest_investment.utils


class Contribution(models.Model):
    user        = models.ForeignKey(User)
    transaction = models.OneToOneField(pynvest_portfolio.models.Transaction)

    def __unicode__(self):
        return u'%s %s %s' % (self.user, self.transaction.date, self.transaction.value())

    @property
    def date(self):
        return self.transaction.date

    def amount(self):
        return self.transaction.value()


class UnitContribution(models.Model):
    contribution = models.OneToOneField(Contribution)
    units        = models.DecimalField(max_digits=18, decimal_places=8)

    def __unicode__(self):
        return u'%s %s' % (self.contribution, self.units)

    @property
    def transaciton(self):
        return self.contribution.transaction

    @property
    def date(self):
        return self.contribution.date

    def amount(self):
        return self.contribution.amount()


class Growth(object):
    def __init__(self, portfolio, user):
        self.portfolio_growth = portfolio.growth()

        all_contribs = UnitContribution.objects.filter(contribution__transaction__lot__portfolio=portfolio).order_by('contribution__transaction__date')
        user_contribs = all_contribs.filter(contribution__user=user)
        user_units = 0
        user_entries = []
        for contrib in user_contribs:
            user_units += contrib.units
            user_entries.append((contrib.date, user_units))

        user_units_lookup = pynvest_investment.utils.BestMatchDict(
                                user_entries, default=0)

        percent_entries = []
        all_units = 0
        for contrib in all_contribs:
            all_units += contrib.units
            percent_entries.append((contrib.date, user_units_lookup[contrib.date] / all_units))

        self.percent_lookup = pynvest_investment.utils.BestMatchDict(
                                  percent_entries, default=0)

    def __iter__(self):
        return iter(self.portfolio_growth)

    def __getitem__(self, date):
        return self.portfolio_growth[date] * self.percent_lookup[date]

    def items(self):
        return [(date, self[date]) for date in self]
