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

    def flatten(self):
        val = [self]

        if len(self.transactions) > 1:
            # TODO: remove special case
            for sub in self.transactions:
                if hasattr(sub, 'flatten'):
                    val.extend(sub.flatten())
                else:
                    val.append(sub)

        return val

    @classmethod
    def from_lot(cls, lot):
        return cls(lot.transaction_set.all())

    @classmethod
    def from_portfolio(cls, portfolio):
        by_lots = [cls.from_lot(lot) for lot in Lot.objects.filter(portfolio=portfolio)]
        grouped = util.groupbyrollup(by_lots, key=operator.attrgetter('investment'))
        return cls([cls(v) for (k, v) in grouped])
