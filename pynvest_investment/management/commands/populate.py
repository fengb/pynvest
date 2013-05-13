import django
import pynvest_connect
from pynvest_investment import models


class Populate(object):
    def __init__(self, investment, fix_existing):
        self.investment = investment
        self.fix_existing = fix_existing

        self.dirty_dates = set()
        self.historicalprices = dict((historicalprice.date, historicalprice) for historicalprice in investment.historicalprice_set.all())
        self.dividends = self._historicalprice_subs(models.Dividend)
        self.splits = self._historicalprice_subs(models.Split)
        self.priceadjustments = self._historicalprice_subs(models.PriceAdjustment)

    @classmethod
    def all(cls, *args, **kwargs):
        populate = cls(*args, **kwargs)
        for func in [populate._prices, populate._dividends, populate._splits, populate._priceadjustment]:
            try:
                func()
            except pynvest_connect.CallNotSupportedException:
                pass
        return populate

    def _historicalprice_subs(self, Model):
        return dict((instance.historicalprice.date, instance)
                        for instance in Model.objects.select_related()
                                                     .filter(historicalprice__investment=self.investment))

    def _prices(self):
        for row in pynvest_connect.historical_prices(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            historicalprice = self.historicalprices.setdefault(row.date, models.HistoricalPrice(investment=self.investment, date=row.date))
            if (historicalprice.high  == row.high and
                historicalprice.low   == row.low and
                historicalprice.close == row.close):
                if self.fix_existing:
                    continue
                else:
                    break

            historicalprice.high = row.high
            historicalprice.low = row.low
            historicalprice.close = row.close
            historicalprice.save()
            self.dirty_dates.add(row.date)

    def _dividends(self):
        for row in pynvest_connect.dividends(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            dividend = self.dividends.setdefault(row.date, models.Dividend(historicalprice=self.historicalprices[row.date]))
            if dividend.amount == row.amount:
                if self.fix_existing:
                    continue
                else:
                    break

            dividend.amount = row.amount
            dividend.save()
            self.dirty_dates.add(row.date)

    def _splits(self):
        for row in pynvest_connect.splits(self.investment.symbol, jurisdiction=self.investment.jurisdiction.symbol):
            split = self.splits.setdefault(row.date, models.Split(historicalprice=self.historicalprices[row.date]))
            if split.before == row.before and split.after == row.after:
                if self.fix_existing:
                    continue
                else:
                    break

            split.before = row.before
            split.after = row.after
            split.save()
            self.dirty_dates.add(row.date)

    def _priceadjustment(self):
        numerator = 1
        denominator = 1

        for date in sorted(self.historicalprices):
            if date in self.dividends:
                numerator *= (self.dividends[date].amount + self.historicalprices[date].close)
                denominator *= self.historicalprices[date].close
            if date in self.splits:
                numerator *= self.splits[date].after
                denominator *= self.splits[date].before

            priceadjustment = self.priceadjustments.setdefault(date, models.PriceAdjustment(historicalprice=self.historicalprices[date]))
            if priceadjustment.raw == float(numerator / denominator):
                continue

            priceadjustment.raw = float(numerator / denominator)
            priceadjustment.save()
            self.dirty_dates.add(date)


class Command(django.core.management.base.BaseCommand):
    help = 'Populates all prices for existing investments'

    def handle(self, *args, **options):
        fix_existing = options.pop('fix_existing', False)
        investments = models.Investment.objects.all()

        num_investments = len(investments)
        for (index, investment) in enumerate(investments):
            if isinstance(investment, basestring):
                investment, created = Investment.objects.get_or_create(symbol=investment, defaults={'name': 'Placeholder'})

            self.stdout.write('%3d/%d %-11s ' % (index + 1, num_investments, investment.symbol), ending='')

            with django.db.transaction.commit_on_success():
                populate = Populate.all(investment, fix_existing)

            if populate.dirty_dates:
                if len(populate.dirty_dates) > 1:
                    self.stdout.write(min(populate.dirty_dates).strftime('%Y-%m-%d - '), ending='')
                self.stdout.write(max(populate.dirty_dates).strftime('%Y-%m-%d'), ending='')

            self.stdout.write('')
