from django.test import TestCase
from pynvest_investment import models

import decimal
import datetime


class TestSnapshot(TestCase):
    def setUp(self):
        exchange = models.Exchange.objects.create(symbol='a', name='b')
        self.investment = models.Investment.objects.create(exchange=exchange, symbol='c', name='d')

    def test_dividend_percent(self):
        snapshot = models.Snapshot(dividend=decimal.Decimal('0.2'), close=20)
        self.assertEquals(snapshot.dividend_percent(), decimal.Decimal('0.01'))

    def test_split(self):
        snapshot = models.Snapshot(split_before=5, split_after=9)
        self.assertEquals(snapshot.split(), '9:5')

    def test_close_adjusted_base(self):
        models.Snapshot.objects.create(investment=self.investment, high=5, low=3, close=4, date=datetime.date.today())

        snapshot = models.Snapshot.objects.close_adjusted()[0]
        self.assertEquals(snapshot.close_adjusted, 4)
