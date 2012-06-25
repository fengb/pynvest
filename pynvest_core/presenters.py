'''Growth interface is any object that supports dict-like read-only interface:
    iter(g)            -> [date, ...] (ascending)
    g[spam]            -> number
    g.items()          -> [(date, number), ...] (ascending by date)

    g.cashflow_dates() -> [date, ...] (ascending)
    g.cashflow_at(d)   -> number
'''


from . import models
import itertools
import operator


DATE = 0
SHARES = 1
VALUE = 2

class InvestmentGrowth(object):
    def __init__(self, investment, entries):
        '''entries is a list of [(date, shares, value), ...]
        '''
        self.investment = investment
        self.entries = entries
        self.start_date = min(map(operator.itemgetter(DATE), entries))
        self.dict_entries = dict((entry[DATE], entry) for entry in entries)

    @classmethod
    def lump_sum(cls, investment, start_value, start_date=None, start_price=None):
        start_date = start_date or investment.historicalprice_set.order_by('date')[0].date
        start_price = start_price or investment.price_at(start_date)
        shares = start_value / start_price

        return cls(investment, [(start_date, shares, start_price)])

    def __iter__(self):
        return iter(self.investment.historicalprice_set.filter(date__gte=self.start_date).order_by('date').values_list('date', flat=True))

    def shares_at(self, target_date):
        return sum(entry[SHARES] for entry in self.entries if entry[DATE] <= target_date)

    def __getitem__(self, date):
        return self.shares_at(date) * self.investment.price_at(date)

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflow_dates(self):
        return map(operator.itemgetter(DATE), self.entries)

    def cashflow_at(self, date):
        if date in self.dict_entries:
            return self.dict_entries[date][VALUE]
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
