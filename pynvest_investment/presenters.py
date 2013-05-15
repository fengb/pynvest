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

    items = [(snapshot.date, snapshot.adjusted('close'))
                 for snapshot in investment.snapshot_set.filter(**filter_args)
                                                        .order_by('date')]

    if start_date and items[0][0] != start_date:
        # hard cutoff at start_date
        items[0] = (start_date, items[0][1])
    return utils.BestMatchDict(items, default=decimal.Decimal(0))


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
        self.shares_finder = utils.BestMatchDict(shares_items, default=decimal.Decimal(0))

    def __iter__(self):
        return iter(self.price_finder)

    def __getitem__(self, date):
        return self.shares_finder[date] * self.price_finder[date]

    def items(self):
        return [(date, self[date]) for date in self]

    def cashflows(self):
        return self._cashflows


def BenchmarkGrowth(growth, investment):
    start_date = next(iter(growth))
    price_finder = PriceFinder(investment, start_date)

    dividends = (models.Dividend.objects.filter(historicalprice__investment=investment, historicalprice__date__gt=start_date)
                                        .order_by('historicalprice__date'))
    dividends = collections.deque(dividends)
    cashflows = collections.deque(growth.cashflows())
    sum_shares = 0
    entries = []
    while cashflows or dividends:
        if cashflows and (not dividends or cashflows[0][0] <= dividends[0].historicalprice.date):
            (date, value) = cashflows.popleft()
            shares = value / price_finder[date]
        else: # if dividends and (not cashflows or dividends[0].date < cashflows[0][0]):
            dividend = dividends.popleft()
            date = dividend.historicalprice.date
            shares = sum_shares * dividend.amount / price_finder[dividend.historicalprice.date]
            value = 0 # reinvested dividends are not from outside thus are not cash values

        sum_shares += shares
        entries.append((date, shares, value))

    return FlatGrowth(entries, price_finder, name=investment.symbol)


def PrincipalGrowth(growth):
    price_finder = utils.BestMatchDict([], default=decimal.Decimal(1))
    return FlatGrowth([(date, cashflow, cashflow) for (date, cashflow) in growth.cashflows()],
                      price_finder=price_finder, name=u'Principal')


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

