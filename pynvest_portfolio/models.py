from django.db import models
import django
import decimal
import operator
import pynvest_investment.models, pynvest_investment.presenters


class Portfolio(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name

    def sell(self, investment, date, shares, price):
        lots = sorted(self.lot_set.filter(investment=investment),
                      key=operator.methodcaller('purchase_date'))

        if sum(l.outstanding_shares for l in lots) + shares < 0:
            raise ValueError('Trying to sell %s shares but only have %s'
                             % (-shares, total_shares))

        with django.db.transaction.commit_on_success():
            transactions = []
            for lot in lots:
                if lot.outstanding_shares <= 0:
                    continue

                transaction = Transaction.objects.create(lot=lot, date=date, price=price,
                                                         shares=max(-lot.outstanding_shares, -shares))
                transactions.append(transaction)
                shares += transaction.shares
                if shares <= 0:
                    break
            return transactions

    def investment_growth(self, investment):
        transactions = Transaction.objects.filter(lot__portfolio=self, lot__investment=investment)

        # Adjustment should not have cashflow value.
        # Switch hasattr to related_default=None once https://code.djangoproject.com/ticket/13839 has been implemented
        entries = [(t.date, t.shares, 0 if hasattr(t, 'adjustment') else t.value())
                       for t in transactions]

        price_finder = pynvest_investment.presenters.PriceFinder(investment, min(entry[0] for entry in entries))
        return pynvest_investment.presenters.FlatGrowth(entries, price_finder=price_finder, name=investment.symbol)

    def growth(self):
        investments = set(lot.investment for lot in self.lot_set.all())
        return pynvest_investment.presenters.AggregateGrowth((self.investment_growth(investment) for investment in investments),
                                                             name=self.name)


class Lot(models.Model):
    investment = models.ForeignKey(pynvest_investment.models.Investment)
    portfolio  = models.ForeignKey(Portfolio)

    def __unicode__(self):
        return u'%s %s' % (self.investment, self.portfolio)

    def base_transaction(self):
        return self.transaction_set.order_by('date')[0]

    def purchase_date(self):
        return self.base_transaction().date

    def purchase_price(self):
        return self.base_transaction().price

    def purchase_value(self):
        return self.purchase_price() * self.outstanding_shares

    def current_price(self):
        return self.investment.current_price()

    def current_value(self):
        return self.current_price() * self.outstanding_shares

    def unrealized_gain(self):
        return (self.current_price() - self.purchase_price()) * self.outstanding_shares

    def unrealized_gain_percent(self):
        return self.unrealized_gain() / self.purchase_value()

    objects = pynvest_investment.managers.QuerySetManager()
    class QuerySet(models.query.QuerySet):
        def from_manager(self):
            return self.annotate(outstanding_shares=models.Sum('transaction__shares'))


class Transaction(models.Model):
    lot    = models.ForeignKey(Lot)
    date   = models.DateField()
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    price  = models.DecimalField(max_digits=12, decimal_places=4)

    def __unicode__(self):
        return u'%s %s %s' % (self.investment, self.date, self.value())

    @property
    def investment(self):
        return self.lot.investment

    def base_transaction(self):
        return self.lot.base_transaction()

    def value(self):
        return self.price * decimal.Decimal(self.shares)

    def realized_gain(self):
        return -self.shares * (self.price - self.base_transaction().price)


class Adjustment(models.Model):
    investment  = models.ForeignKey(pynvest_investment.models.Investment)
    transaction = models.OneToOneField(Transaction)
    reason      = models.CharField(max_length=3, choices=[
                        ('div', 'dividend'),
                        ('cst', 'capital gains short-term'),
                        ('clt', 'capital gains long-term'),
                        ('fee', 'fee'),
                        ('tax', 'tax'),
                        ('exp', 'expense'),
                      ])
    memo        = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.reason, self.transaction)

    def date(self):
        return self.transaction.date

    def value(self):
        return self.transaction.value()
