'''Growth interface is any object that supports dict-like read-only interface:
    iter(g)            -> [date, ...] (ascending)
    g[spam]            -> number
    g.items()          -> [(date, number), ...] (ascending by date)

    g.cashflows() -> [(date, number), ...] (ascending by date)
'''


from . import models, utils
import itertools
import operator
import collections
import decimal


def PriceFinder(investment, start_date=None):
    filter_args = {}
    if start_date:
        # start_date may not have a price entry.  We need to backtrack to find the real start date.
        search_start_date = investment.historicalprice_set.filter(date__lte=start_date).latest('date').date
        filter_args['date__gte'] = search_start_date

    items = list(investment.historicalprice_set.filter(**filter_args).order_by('date').values_list('date', 'close'))

    if start_date and items[0][0] != start_date:
        # hard cutoff at start_date
        items[0] = (start_date, items[0][1])
    return utils.BinarySearchThing(items)


class InvestmentGrowth(object):
    def __init__(self, investment, entries, price_finder=None):
        '''entries - [(date, shares, value), ...]'''
        self.investment = investment
        self.start_date = min(entry[0] for entry in entries)
        self.price_finder = price_finder or PriceFinder(self.investment, self.start_date)
        self._cashflows = sorted([(date, value) for (date, shares, value) in entries], key=operator.itemgetter(0))

        shares_items = []
        sum = decimal.Decimal()
        for (date, shares, value) in sorted(entries):
            sum += shares
            shares_items.append((date, sum))
        self.shares_finder = utils.BinarySearchThing(shares_items)

    @classmethod
    def lump_sum(cls, investment, start_date, start_value):
        return cls.lump_sums(investment, [(start_date, start_value)])

    @classmethod
    def lump_sums(cls, investment, entries):
        '''entries is a list of [(date, value), ...]'''
        price_finder = PriceFinder(investment, min(entry[0] for entry in entries))
        growth_entries = [(date, value / price_finder[date], value) for (date, value) in entries]
        return cls(investment, growth_entries, price_finder=price_finder)

    @classmethod
    def benchmark(cls, investment, growth):
        return cls.lump_sums(investment, growth.cashflows())

    def __iter__(self):
        return iter(self.price_finder)

    def __getitem__(self, date):
        if date < self.start_date:
            return 0

        return self.shares_finder[date] * self.price_finder[date]

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflows(self):
        return self._cashflows


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
        all_cashflows = collections.defaultdict(0)
        for growth in self.subgrowths:
            for (date, value) in growth.cashflows():
                all_cashflows[date] += value

        return sorted(all_cashflows.items())
