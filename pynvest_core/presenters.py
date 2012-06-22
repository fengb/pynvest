'''Growth interface is any object that supports dict-like read-only interface:
    iter(g)            -> [date, ...] (ascending)
    g[spam]            -> number
    g.items()          -> [(date, number), ...] (ascending by date)

    g.cashflow_dates() -> [date, ...] (ascending)
    g.cashflow_at(d)   -> number
'''


from . import models
import itertools


class InvestmentGrowth(object):
    '''Required subclass responsibilities:
        investment
        start_date
        shares_at(date)
        cashflow_dates()
        cashflow_at(d)
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

    def cashflow_dates(self):
        raise NotImplemented

    def cashflow_at(self, date):
        raise NotImplemented


class LumpSumGrowth(InvestmentGrowth):
    def __init__(self, investment, start_value, start_date=None, start_price=None):
        self.investment = investment
        self.start_value = start_value
        self.start_date = start_date or self.investment.historicalprice_set.order_by('date')[0].date
        self.start_price = start_price or self.investment.price_at(self.start_date)

        self.shares = self.start_value / self.start_price

    def shares_at(self, date):
        return self.shares

    def cashflow_dates(self):
        return [self.start_date]

    def cashflow_at(self, date):
        if date == self.start_date:
            return self.start_value
        return 0


class AggregateGrowth(object):
    def __init__(self, growths):
        self.subgrowths = list(growths)

    def iter_order_unique(self, *growths):
        values = set(itertools.chain(*growths))
        return iter(sorted(values))

    def __iter__(self):
        return self.iter_order_unique(*self.subgrowths)

    def __getitem__(self, date):
        return sum(g[date] for g in self.subgrowths)

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflow_dates(self):
        return self.iter_order_unique(*[g.cashflow_dates() for g in self.subgrowths])

    def cashflow_at(self, date):
        return sum(g.cashflow_at(date) for g in self.subgrowths)
