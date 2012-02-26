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
    def first_trade_date(self):
        return min(transaction.trade_date
                     for transaction in self.transactions)

    @property
    def last_trade_date(self):
        return max(transaction.trade_date
                     for transaction in self.transactions)

    @property
    def purchase_price(self):
        return self.transactions[0].price

    @property
    def shares(self):
        return sum(transaction.shares
                     for transaction in self.transactions)

    @classmethod
    def for_portfolio_by_investment(cls, portfolio):
        transactions = Transaction.objects.filter(lot__portfolio=portfolio)
        grouped = util.groupbyrollup(transactions, key=operator.attrgetter('investment'))
        return [cls(v) for (k, v) in grouped]

    @classmethod
    def for_portfolio_by_lot(cls, portfolio):
        return [cls(lot.transaction_set.all())
                 for lot in Lot.objects.filter(portfolio=portfolio)]
