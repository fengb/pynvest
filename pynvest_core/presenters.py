'''Growth interface is any object that supports dict-like read-only interface:
    g[spam]   -> number
    iter(g)   -> date (sorted ascending order)
'''


from . import models
import itertools


class InvestmentGrowth(object):
    '''Required subclass responsibilities:
        investment
        start_date
        shares_at(date)
    '''
    def __init__(self, *args, **kwargs):
        raise NotImplemented

    def shares_at(self, date):
        raise NotImplemented

    def __iter__(self):
        return iter(self.investment.historicalprice_set.filter(date__gte=self.start_date).order_by('date').values_list('date', flat=True))

    def __getitem__(self, date):
        if date < self.start_date:
            return 0

        return self.shares_at(date) * self.investment.price_at(date)

    def items(self):
        return [(date, self[date]) for date in self]


class LumpSumGrowth(InvestmentGrowth):
    def __init__(self, investment, start_value, start_date=None, start_price=None):
        self.investment = investment
        self.start_value = start_value
        self.start_date = start_date or self.investment.historicalprice_set.order_by('date')[0].date
        self.start_price = start_price or self.investment.price_at(self.start_date)

        self.shares = self.start_value / self.start_price

    def shares_at(self, date):
        return self.shares


class AggregateGrowth(object):
    def __init__(self, growths):
        self.subgrowths = list(growths)

    @classmethod
    def iter_order_unique(cls, *growths):
        values = set(itertools.chain(*growths))
        return iter(sorted(values))

    def __iter__(self):
        return AggregateGrowth.iter_order_unique(*self.subgrowths)

    def __getitem__(self, date):
        return sum(g[date] for g in self.subgrowths)
