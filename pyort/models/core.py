from .. import util
from . import Portfolio, Lot, Transaction
import operator


class TransactionAggregate(object):
    def __init__(self, transactions):
        self.transactions = list(transactions)

    @property
    def investment(self):
        return self.transactions[0].investment

    @property
    def trade_date(self):
        return min(t.trade_date for t in self.transactions)

    @property
    def shares(self):
        return sum(t.shares for t in self.transactions)

    @property
    def price(self):
        # Weighted average of purchase prices
        purchase_transactions = filter(lambda x: x.shares > 0, self.transactions)
        return (sum(t.price * t.shares for t in purchase_transactions) /
                sum(t.shares for t in purchase_transactions))

    @classmethod
    def for_portfolio_by_investment(cls, portfolio):
        by_lots = cls.for_portfolio_by_lot(portfolio)
        grouped = util.groupbyrollup(by_lots, key=operator.attrgetter('investment'))
        return [cls(v) for (k, v) in grouped]

    @classmethod
    def for_portfolio_by_lot(cls, portfolio):
        return [cls(lot.transaction_set.all())
                 for lot in Lot.objects.filter(portfolio=portfolio)]
