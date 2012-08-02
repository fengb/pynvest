'''Growth interface is any object that supports dict-like read-only interface:
    name               -> name of the growth
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
        search_start_date = investment.snapshot_set.filter(date__lte=start_date).latest('date').date
        filter_args['date__gte'] = search_start_date

    items = list(investment.snapshot_set.filter(**filter_args).order_by('date').values_list('date', 'close'))

    if start_date and items[0][0] != start_date:
        # hard cutoff at start_date
        items[0] = (start_date, items[0][1])
    return utils.BinarySearchThing(items, default=decimal.Decimal(0))


class FlatGrowth(object):
    def __init__(self, entries, price_finder, name=None):
        '''entries - [(date, shares, value), ...]'''
        self.name = name
        self.price_finder = price_finder

        self._cashflows = sorted([(date, value) for (date, shares, value) in entries], key=operator.itemgetter(0))

        shares_items = []
        sum = decimal.Decimal()
        for (date, shares, value) in sorted(entries):
            sum += shares
            shares_items.append((date, sum))
        self.shares_finder = utils.BinarySearchThing(shares_items, default=decimal.Decimal(0))

    def __iter__(self):
        return iter(self.price_finder)

    def __getitem__(self, date):
        return self.shares_finder[date] * self.price_finder[date]

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflows(self):
        return self._cashflows


def InvestmentGrowth(investment, entries):
    price_finder = PriceFinder(investment, min(entry[0] for entry in entries))
    return FlatGrowth(entries, price_finder=price_finder, name=investment.symbol)


class AggregateGrowth(object):
    def __init__(self, growths, name=None):
        self.name = name
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
        all_cashflows = collections.defaultdict(int)
        for growth in self.subgrowths:
            for (date, value) in growth.cashflows():
                all_cashflows[date] += value

        return sorted(all_cashflows.items())

    def benchmark(self, investment):
        price_finder = PriceFinder(investment, next(iter(self)))
        entries = [(date, value / price_finder[date], value) for (date, value) in self.cashflows()]
        return FlatGrowth(entries, price_finder, name=investment.symbol)

    def principal(self):
        price_finder = utils.BinarySearchThing([], default=decimal.Decimal(1))
        return FlatGrowth([(date, cashflow, cashflow) for (date, cashflow) in self.cashflows()],
                          price_finder=price_finder, name=u'Principal')
