'''Growth interface is any object that supports dict-like read-only interface:
    iter(g)            -> [date, ...] (ascending)
    g[spam]            -> number
    g.items()          -> [(date, number), ...] (ascending by date)

    g.cashflows() -> [(date, number), ...] (ascending by date)
'''


from . import models
import itertools
import operator
import collections
import decimal


DATE = 0
SHARES = 1
VALUE = 2

class InvestmentGrowth(object):
    def __init__(self, investment, entries):
        '''entries is a list of [(date, shares, value), ...]'''
        self.investment = investment
        self.entries = entries
        self.start_date = min(map(operator.itemgetter(DATE), entries))
        self.dict_entries = dict((entry[DATE], entry) for entry in entries)

    @classmethod
    def lump_sum(cls, investment, start_date, start_value):
        return cls.lump_sums(investment, [(start_date, start_value)])

    @classmethod
    def lump_sums(cls, investment, entries):
        '''entries is a list of [(date, value), ...]'''
        growth_entries = [(date, value / investment.price_at(date), value) for (date, value) in entries]
        return cls(investment, growth_entries)

    @classmethod
    def benchmark(cls, investment, growth):
        return cls.lump_sums(investment, growth.cashflows())

    def __iter__(self):
        return iter(self.investment.historicalprice_set.filter(date__gte=self.start_date).order_by('date').values_list('date', flat=True))

    def shares_at(self, target_date):
        return sum(entry[SHARES] for entry in self.entries if entry[DATE] <= target_date)

    def __getitem__(self, date):
        return self.shares_at(date) * self.investment.price_at(date)

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflows(self):
        return [(entry[DATE], entry[VALUE]) for entry in self.entries]


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

    def cashflows(self):
        all_cashflows = collections.defaultdict(decimal.Decimal)
        for growth in self.subgrowths:
            for (date, value) in growth.cashflows():
                all_cashflows[date] += value

        return sorted(all_cashflows.items())
