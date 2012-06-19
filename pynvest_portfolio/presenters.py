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


class LotGrowth(object):
    def __init__(self, lot):
        self.lot = lot

    def value_at(self, date):
        aggregate = self.lot.transaction_set.filter(date__lte=date).aggregate(django.db.models.Sum('shares'))
        shares = aggregate['shares__sum'] or 0
        return shares * self.lot.investment.price_at(date)


def PortfolioGrowth(portfolio):
    lots = portfolio.lot_set.all()
    return pynvest_core.presenters.GrowthAggregate(map(LotGrowth, lots))
