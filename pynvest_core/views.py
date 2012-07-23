from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import datetime
import decimal


def investment_snapshots(request, symbol, year=None, month=None, day=None):
    investment = get_object_or_404(models.Investment, symbol=symbol)
    end_date = datetime.date(int(year), int(month), int(day)) if year else datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)

    return render_to_response('pynvest_core/snapshots_table.html', {
        'title': investment.symbol,
        'snapshots': investment.snapshot_set.filter(date__gte=start_date, date__lte=end_date).order_by('-date'),
    })


def investment_growth(request, symbol):
    investment = get_object_or_404(models.Investment, symbol=symbol)

    return render_to_response('pynvest_core/growth_table.html', {
        'title': investment.symbol,
        'growth': presenters.InvestmentGrowth.lump_sum(investment, start_date=investment.snapshot_set.order_by('date')[0].date,
                                                                   start_value=decimal.Decimal(10000))
    })
