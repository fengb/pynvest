class TransactionAggregate(object):
    def __init__(self, transactions):
        self.transactions = list(transactions)

    def investment(self):
        return self.transactions[0].investment

    def created_date(self):
        return min(transaction.date
                     for transaction in self.transactions)

    def updated_date(self):
        return max(transaction.date
                     for transaction in self.transactions)

    def shares(self):
        return sum(transaction.shares
                     for transaction in self.transactions)

