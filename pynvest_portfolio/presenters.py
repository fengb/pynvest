from . import models, util
import django.db
import pynvest_core.presenters
import operator


class LotSummary(object):
    def __init__(self, lots):
        if len(lots) < 1:
            raise ValueError

        self.lots = lots

    def _unique_field(self, field):
        values = map(operator.attrgetter(field), self.lots)
        if len(set(values)) > 1:
            return None
        return values[0]

    def _unique_callable(self, field):
        values = [getattr(lot, field)() for lot in self.lots]
        if len(set(values)) > 1:
            return None
        return values[0]

    def investment(self):
        return self._unique_field('investment')

    def purchase_date(self):
        return self._unique_callable('purchase_date')

    def purchase_price(self):
        return self._unique_callable('purchase_price')

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
