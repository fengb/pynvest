from . import models, util
import django.db
import pynvest_core.presenters
import operator


class LotSummary(object):
    def __init__(self, lots):
        if len(lots) < 1:
            raise ValueError
        if len(set(l.investment for l in lots)) > 1:
            raise ValueError

        self.lots = lots

    def investment(self):
        return self.lots[0].investment

    def outstanding_shares(self):
        return sum(l.outstanding_shares for l in self.lots)

    def current_price(self):
        return self.investment().current_price()

    def current_value(self):
        return sum(l.current_value() for l in self.lots)

    @classmethod
    def group_by_investment(cls, lots):
        return [cls(ls) for (investment, ls) in util.groupbyrollup(lots, key=operator.attrgetter('investment'))]


class PortfolioInvestmentGrowth(pynvest_core.presenters.InvestmentGrowth):
    def __init__(self, portfolio, investment):
        self.transactions = models.Transaction.objects.filter(lot__portfolio=portfolio, lot__investment=investment)

        self.investment = investment
        # Why isn't there an 'earliest' method? :(
        self.start_date = self.transactions.order_by('date')[:1].get().date

    def shares_at(self, date):
        aggregate = self.transactions.filter(date__lte=date).aggregate(django.db.models.Sum('shares'))
        return aggregate['shares__sum'] or 0


def PortfolioGrowth(portfolio):
    investments = set(lot.investment for lot in portfolio.lot_set.all())
    return pynvest_core.presenters.AggregateGrowth(PortfolioInvestmentGrowth(portfolio, investment) for investment in investments)
