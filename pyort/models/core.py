class TransactionAggregate(object):
    def __init__(self, transactions):
        self.transactions = list(transactions)

    @property
    def investment(self):
        return self.transactions[0].investment

    @property
    def trade_date(self):
        return max(transaction.trade_date
                     for transaction in self.transactions)

    @property
    def shares(self):
        return sum(transaction.shares
                     for transaction in self.transactions)

