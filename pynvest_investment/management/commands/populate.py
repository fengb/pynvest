import django
import pynvest_connect
from pynvest_investment import models


class Populate(object):
    def __init__(self, investment):
        self.investment = investment

        self.dirty_dates = set()
        self.historicalprices = dict((historicalprice.date, historicalprice) for historicalprice in investment.historicalprice_set.all())
        self.dividends = self._historicalprice_subs(models.Dividend)
        self.splits = self._historicalprice_subs(models.Split)
        self.priceadjustments = self._historicalprice_subs(models.PriceAdjustment)

    @classmethod
    def all(cls, *args, **kwargs):
        populate = cls(*args, **kwargs)
        populate._prices()
        populate._dividends()
        populate._splits()
        populate._priceadjustments()
        return populate

    def _historicalprice_subs(self, model):
        return dict((instance.historicalprice.date, instance)
                        for instance in model.objects.select_related()
                                                     .filter(historicalprice__investment=self.investment))

    def _prices(self):
        for row in pynvest_connect.historical_prices(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            if row.date in self.historicalprices:
                break
            self.historicalprices[row.date] = models.HistoricalPrice.objects.create(
                                                  investment=self.investment,
                                                  date=row.date,
                                                  high=row.high,
                                                  low=row.low,
                                                  close=row.close
                                              )
            self.dirty_dates.add(row.date)

    def _dividends(self):
        for row in pynvest_connect.dividends(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            if row.date in self.dividends:
                break
            self.dividends[row.date] = models.Dividend.objects.create(
                                           historicalprice=self.historicalprices[row.date],
                                           amount=row.amount
                                       )
            self.dirty_dates.add(row.date)

    def _splits(self):
        for row in pynvest_connect.splits(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            if row.date in self.splits:
                break
            self.splits[row.date] = models.Split.objects.create(
                                        historicalprice=self.historicalprices[row.date],
                                        before=row.before,
                                        after=row.after
                                    )
            self.dirty_dates.add(row.date)

    def _priceadjustments(self):
        if self.priceadjustments:
            dates = sorted(set(self.historicalprices) - set(self.priceadjustments))
            last_raw = self.priceadjustments[max(self.priceadjustments)].raw
        else:
            dates = sorted(self.historicalprices)
            last_raw = 1.0

        for date in dates:
            if date in self.dividends:
                last_raw *= float(self.dividends[date].amount + self.historicalprices[date].close) / float(self.historicalprices[date].close)
            if date in self.splits:
                last_raw *= float(self.splits[date].after) / self.splits[date].before

            self.priceadjustments[date] = models.PriceAdjustment.objects.create(
                                              historicalprice=self.historicalprices[date],
                                              raw=last_raw
                                          )
            self.dirty_dates.add(date)


class Command(django.core.management.base.BaseCommand):
    help = 'Populates all prices for existing investments'

    def handle(self, *args, **options):
        investments = models.Investment.objects.all()

        num_investments = len(investments)
        for (index, investment) in enumerate(investments):
            if isinstance(investment, basestring):
                investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

            self.stdout.write('%3d/%d %-11s ' % (index + 1, num_investments, investment.symbol), ending='')

            with django.db.transaction.commit_on_success():
                populate = Populate.all(investment)

            if populate.dirty_dates:
                if len(populate.dirty_dates) > 1:
                    self.stdout.write(min(populate.dirty_dates).strftime('%Y-%m-%d - '), ending='')
                self.stdout.write(max(populate.dirty_dates).strftime('%Y-%m-%d'), ending='')

            self.stdout.write('')
