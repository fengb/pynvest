from . import models
import django.db
import pynvest_investment.presenters
import operator
import itertools


class LotSummary(object):
    def __init__(self, lots):
        lots = list(lots)
        if len(lots) < 1:
            raise ValueError

        self.lots = lots

    def _values(self, field):
        base = getattr(self.lots[0], field)
        if callable(base):
            return map(operator.methodcaller(field), self.lots)
        else:
            return map(operator.attrgetter(field), self.lots)

    def _unique_field(self, field):
        values = self._values(field)
        if len(set(values)) > 1:
            return None
        return values[0]

    def _sum_field(self, field):
        return sum(self._values(field))

    def portfolio(self):
        return self._unique_field('portfolio')

    def investment(self):
        return self._unique_field('investment')

    def purchase_date(self):
        return self._unique_field('purchase_date')

    def purchase_price(self):
        return self._unique_field('purchase_price')

    def outstanding_shares(self):
        return self._sum_field('outstanding_shares')

    def current_price(self):
        return self._unique_field('current_price')

    def current_value(self):
        return self._sum_field('current_value')

    def unrealized_gain(self):
        return self._sum_field('unrealized_gain')

    def unrealized_gain_percent(self):
        purchase_value = self._sum_field('purchase_value')
        if purchase_value:
            return self.unrealized_gain() / purchase_value
        else:
            return 0

    @classmethod
    def group_by_investment(cls, lots):
        lots = sorted(lots, key=lambda x: x.purchase_date())
        keyfunc = lambda x: x.investment.symbol
        lots.sort(key=keyfunc)
        return [cls(ls) for (investment, ls) in itertools.groupby(lots, key=keyfunc)]
