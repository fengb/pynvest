from . import models, util
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
        if len(self.transactions) == 1:
            return self.transactions[0].price

        if self.shares == 0:
            return 0

        # Weighted average of purchase prices
        purchase_transactions = filter(lambda x: x.shares > 0, self.transactions)
        return (sum(t.price * t.shares for t in purchase_transactions) /
                sum(t.shares for t in purchase_transactions))

    def flatten(self, level=0, include_self=False):
        self.level = level
        val = [self] if include_self else []

        if len(self.transactions) > 1:
            for sub in self.transactions:
                val.extend(sub.flatten(level + 1, True))

        return val

    @classmethod
    def from_transaction(cls, transaction):
        return cls([transaction])

    @classmethod
    def from_lot(cls, lot):
        return cls(cls([t]) for t in lot.transaction_set.all())

    @classmethod
    def from_portfolio(cls, portfolio):
        by_lots = [cls.from_lot(lot) for lot in models.Lot.objects.filter(portfolio=portfolio)]
        grouped = util.groupbyrollup(by_lots, key=operator.attrgetter('investment'))
        return cls([cls(v) for (k, v) in grouped])


class TransactionSummary(object):
    def __init__(self, transactions):
        if len(transactions) < 1:
            raise ValueError
        if len(set(t.investment for t in transactions)) > 1:
            raise ValueError

        self.transactions = transactions

    def investment(self):
        return self.transactions[0].investment

    def shares(self):
        return sum(t.shares for t in self.transactions)

    @classmethod
    def group_by_lot(cls, transactions):
        return [cls(ts) for (lot, ts) in util.groupbyrollup(transactions, key=operator.attrgetter('lot'))]

    @classmethod
    def group_with_purchase(cls, transactions):
        return [cls([t.lot.purchase_transaction(), t]) for t in transactions]
