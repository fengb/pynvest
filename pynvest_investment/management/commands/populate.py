import django
import pynvest_connect
from pynvest_investment import models


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

            dirty_dates = set()
            with django.db.transaction.commit_on_success():
                historicalprices = dict((historicalprice.date, historicalprice) for historicalprice in investment.historicalprice_set.all())
                for func in [self._populate_prices, self._populate_dividends, self._populate_splits]:
                    try:
                        dirty_dates.update(func(investment, fix_existing, historicalprices))
                    except pynvest_connect.CallNotSupportedException:
                        pass

            if dirty_dates:
                if len(dirty_dates) > 1:
                    self.stdout.write(min(dirty_dates).strftime('%Y-%m-%d - '), ending='')
                self.stdout.write(max(dirty_dates).strftime('%Y-%m-%d'), ending='')

            self.stdout.write('')

    def _populate_prices(self, investment, fix_existing, historicalprices):
        dirty_dates = set()
        for row in pynvest_connect.historical_prices(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
            historicalprice = historicalprices.setdefault(row.date, models.HistoricalPrice(investment=investment, date=row.date))
            if (historicalprice.high  == row.high and
                historicalprice.low   == row.low and
                historicalprice.close == row.close):
                if fix_existing:
                    continue
                else:
                    break

            historicalprice.high = row.high
            historicalprice.low = row.low
            historicalprice.close = row.close
            historicalprice.save()
            dirty_dates.add(row.date)
        return dirty_dates

    def _populate_dividends(self, investment, fix_existing, historicalprices):
        dividends = dict((dividend.historicalprice.date, dividend)
                             for dividend in models.Dividend.objects.select_related()
                                                                    .filter(historicalprice__investment=investment))
        dirty_dates = set()
        for row in pynvest_connect.dividends(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
            dividend = dividends.setdefault(row.date, models.Dividend(historicalprice=historicalprices[row.date]))
            if dividend.amount == row.amount:
                if fix_existing:
                    continue
                else:
                    break

            dividend.amount = row.amount
            dividend.save()
            dirty_dates.add(row.date)
        return dirty_dates

    def _populate_splits(self, investment, fix_existing, historicalprices):
        splits = dict((split.historicalprice.date, split)
                          for split in models.Split.objects.select_related()
                                                           .filter(historicalprice__investment=investment))
        dirty_dates = set()
        for row in pynvest_connect.splits(investment.symbol, jurisdiction=investment.jurisdiction.symbol):
            split = splits.setdefault(row.date, models.Split(historicalprice=historicalprices[row.date]))
            if split.before == row.before and split.after == row.after:
                if fix_existing:
                    continue
                else:
                    break

            split.before = row.before
            split.after = row.after
            split.save()
            dirty_dates.add(row.date)
        return dirty_dates
