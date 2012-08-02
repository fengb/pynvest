from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import datetime
import decimal


def investment(request, symbol):
    investment = get_object_or_404(models.Investment, symbol=symbol)

    return render_to_response('pynvest_core/investment.html', {
        'title': investment.symbol,
        'investment': investment,
    })


def investment_snapshots(request, symbol, year=None, month=None, day=None):
    investment = get_object_or_404(models.Investment, symbol=symbol)
    end_date = datetime.date(int(year), int(month), int(day)) if year else datetime.date.today()

    return render_to_response('pynvest_core/snapshots_table.html', {
        'title': investment.symbol,
        'snapshots': investment.snapshot_set.filter_year_range(end_date=end_date).order_by('-date'),
    })
