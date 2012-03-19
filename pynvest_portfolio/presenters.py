from . import models, util
import operator


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
    def group_by_investment(cls, transactions):
        return [cls(ts) for (investment, ts) in util.groupbyrollup(transactions, key=operator.attrgetter('investment'))]
