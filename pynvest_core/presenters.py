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


InvestmentGrowthEntry = collections.namedtuple('GrowthEntry', 'date shares value')

class InvestmentGrowth(object):
    def __init__(self, investment, entries):
        self.investment = investment
        self.entries = entries
        self.start_date = min(map(operator.attrgetter('date'), self.entries))

    @classmethod
    def lump_sum(cls, investment, start_date, start_value):
        return cls.lump_sums(investment, [(start_date, start_value)])

    @classmethod
    def lump_sums(cls, investment, entries):
        '''entries is a list of [(date, value), ...]'''
        growth_entries = [InvestmentGrowthEntry(date, value / investment.price_at(date), value) for (date, value) in entries]
        return cls(investment, growth_entries)

    @classmethod
    def benchmark(cls, investment, growth):
        return cls.lump_sums(investment, growth.cashflows())

    def __iter__(self):
        return iter(self.investment.historicalprice_set.filter(date__gte=self.start_date).order_by('date').values_list('date', flat=True))

    def shares_at(self, target_date):
        return sum(entry.shares for entry in self.entries if entry.date <= target_date)

    def __getitem__(self, date):
        return self.shares_at(date) * self.investment.price_at(date)

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflows(self):
        return [(entry.date, entry.value) for entry in self.entries]


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
