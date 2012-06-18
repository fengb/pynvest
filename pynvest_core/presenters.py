from . import models


class Growth(object):
    def __init__(self, investment, start_date, start_value):
        self.investment = investment
        self.start_date = start_date
        self.start_value = start_value

        self.shares = self.start_value / self.investment.price_at(start_date)

    def value_at(self, date):
        return self.shares * self.investment.price_at(date)
