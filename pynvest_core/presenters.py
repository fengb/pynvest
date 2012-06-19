from . import models


class Growth(object):
    def __init__(self, investment, start_date, start_value, start_price=None):
        self.investment = investment
        self.start_date = start_date
        self.start_value = start_value
        self.start_price = start_price or self.investment.price_at(start_date)

        self.shares = self.start_value / self.start_price

    def value_at(self, date):
        if date < self.start_date:
            return 0

        return self.shares * self.investment.price_at(date)


class GrowthAggregate(object):
    def __init__(self, growths):
        self.subgrowths = list(growths)

    def value_at(self, date):
        return sum(g.value_at(date) for g in self.subgrowths)
