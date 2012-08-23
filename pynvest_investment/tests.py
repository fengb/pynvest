from django.test import TestCase
from pynvest_investment import models

import decimal
import datetime


class TestSnapshot(TestCase):
    def test_dividend_percent(self):
        snapshot = models.Snapshot(dividend=decimal.Decimal('0.2'), close=20)
        self.assertEquals(snapshot.dividend_percent(), decimal.Decimal('0.01'))

    def test_split(self):
        snapshot = models.Snapshot(split_before=5, split_after=9)
        self.assertEquals(snapshot.split(), '9:5')

class TestSnapshotCloseAdjusted(TestCase):
    def setUp(self):
        exchange = models.Exchange.objects.create(symbol='a', name='b')
        self.investment = models.Investment.objects.create(exchange=exchange, symbol='c', name='d')

    def create_snapshot(self, **kwargs):
        data = {'investment': self.investment, 'high': 100, 'low': 1, 'close': 10, 'date': datetime.date.today()}
        data.update(kwargs)
        return models.Snapshot.objects.create(**data)

    def assertCloseAdjusted(self, snapshot, value):
        snapshot = models.Snapshot.objects.close_adjusted().get(id=snapshot.id)
        self.assertEquals(round(snapshot.close_adjusted, 4), value)

    def test_standalone_is_close(self):
        '''Standalone snapshot always has close_adjusted == close'''
        snapshot0 = self.create_snapshot(dividend=1.2345, split_before=1, split_after=42)

        self.assertCloseAdjusted(snapshot0, snapshot0.close)

    def test_split_adjusts_close_as_multiple(self):
        '''Example split calculation:
        Date        Price  Split  Adj.Price
        2012-04-03     10    2:1      10.00
        2012-04-02     20              9.00
        2012-04-01     21              9.50
        '''
        snapshot0 = self.create_snapshot(close=10, split_before=1, split_after=2)
        snapshot1 = self.create_snapshot(close=10, date=(datetime.date.today() - datetime.timedelta(1)))

        self.assertCloseAdjusted(snapshot1, 5)

    def test_dividend_adjusts_close_based_on_percentage(self):
        '''Example dividend calculation:
        Date        Price  Div  Adj.Price
        2012-04-03      9    1       9.00
        2012-04-02     10            9.00
        2012-04-01      9            8.10

        Explanation:  Spinning off $1 while dropping the price by $1 actually
        keeps the value identical to before.  Because we need to keep this
        "change" constant, the adjusted price of past snapshots must drop to
        90%.  Multiplier = p[n] / (p[n] + d[n])
        '''
        snapshot0 = self.create_snapshot(close=9, dividend=1)
        snapshot1 = self.create_snapshot(close=10, date=(datetime.date.today() - datetime.timedelta(1)))
        snapshot2 = self.create_snapshot(close=9, date=(datetime.date.today() - datetime.timedelta(2)))

        self.assertCloseAdjusted(snapshot1, 9)
        self.assertCloseAdjusted(snapshot2, 8.1)

    def test_multiple_events(self):
        '''Example:
        Date        Price  Div  Split  Adj.Price
        2012-04-04      9    1              9.00
        2012-04-03     10         2:1       9.00
        2012-04-02     20                   9.00
        2012-04-01     22                   9.90
        '''
        base = self.create_snapshot(close=9, dividend=1)
        snapshot1 = self.create_snapshot(close=10, split_before=1, split_after=2, date=(datetime.date.today() - datetime.timedelta(1)))
        snapshot2 = self.create_snapshot(close=20, date=(datetime.date.today() - datetime.timedelta(2)))
        snapshot3 = self.create_snapshot(close=22, date=(datetime.date.today() - datetime.timedelta(3)))

        self.assertCloseAdjusted(snapshot1, 9)
        self.assertCloseAdjusted(snapshot2, 9)
        self.assertCloseAdjusted(snapshot3, 9.9)
