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

    def test_standalone_is_close(self):
        snapshot = self.create_snapshot()
        snapshot = models.Snapshot.objects.close_adjusted().get(id=snapshot.id)
        self.assertEquals(snapshot.close_adjusted, snapshot.close)

    def test_split_adjusts_close_as_multiple(self):
        self.create_snapshot(close=10, split_before=1, split_after=2)
        snapshot = self.create_snapshot(close=10, date=(datetime.date.today() - datetime.timedelta(1)))

        snapshot = models.Snapshot.objects.close_adjusted().get(id=snapshot.id)
        self.assertEquals(snapshot.close_adjusted, 5)
