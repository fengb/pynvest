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
import bisect


class PriceFinder(object):
    def __init__(self, investment, start_date=None):
        filter_args = {'investment': investment}
        if start_date:
            filter_args['date__gte'] = start_date
        self.dates_prices = list(models.HistoricalPrice.objects.filter(**filter_args).order_by('date').values_list('date', 'close'))

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        return map(operator.itemgetter(0), self.dates_prices)

    def __getitem__(self, date):
        # Make sure this fake value is always greater than the search value such that (sdate, svalue) < (date, value) when sdate == date
        value = decimal.Decimal('inf')
        i = bisect.bisect(self.dates_prices, (date, value))

        # i points at match + 1
        return self.dates_prices[i - 1][1]


InvestmentGrowthEntry = collections.namedtuple('GrowthEntry', 'date shares value')

class InvestmentGrowth(object):
    def __init__(self, investment, entries, price_finder=None):
        self.investment = investment
        self.entries = entries
        self.start_date = min(entry.date for entry in entries)
        self.price_finder = price_finder or PriceFinder(self.investment, self.start_date)

    @classmethod
    def lump_sum(cls, investment, start_date, start_value):
        return cls.lump_sums(investment, [(start_date, start_value)])

    @classmethod
    def lump_sums(cls, investment, entries):
        '''entries is a list of [(date, value), ...]'''
        price_finder = PriceFinder(investment, min(entry[0] for entry in entries))
        growth_entries = [InvestmentGrowthEntry(date, value / price_finder[date], value) for (date, value) in entries]
        return cls(investment, growth_entries, price_finder=price_finder)

    @classmethod
    def benchmark(cls, investment, growth):
        return cls.lump_sums(investment, growth.cashflows())

    def __iter__(self):
        return iter(key for key in self.price_finder.keys() if key >= self.start_date)

    def shares_at(self, target_date):
        return sum(entry.shares for entry in self.entries if entry.date <= target_date)

    def __getitem__(self, date):
        return self.shares_at(date) * self.price_finder[date]

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
