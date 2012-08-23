from django.test import TestCase
from pynvest_investment import models

import decimal
import datetime


class TestSnapshot(TestCase):
    def setUp(self):
        exchange = models.Exchange.objects.create(symbol='a', name='b')
        self.investment = models.Investment.objects.create(exchange=exchange, symbol='c', name='d')

    def create_snapshot(self, **kwargs):
        data = {'investment': self.investment, 'high': 100, 'low': 1, 'close': 10, 'date': datetime.date.today()}
        data.update(kwargs)
        return models.Snapshot.objects.create(**data)

    def test_dividend_percent(self):
        snapshot = self.create_snapshot(dividend=decimal.Decimal('0.2'), close=20)
        self.assertEquals(snapshot.dividend_percent(), decimal.Decimal('0.01'))

    def test_split(self):
        snapshot = self.create_snapshot(split_before=5, split_after=9)
        self.assertEquals(snapshot.split(), '9:5')

    def test_close_adjusted_base(self):
        self.create_snapshot(close=4)

        snapshot = models.Snapshot.objects.close_adjusted()[0]
        self.assertEquals(snapshot.close_adjusted, 4)
