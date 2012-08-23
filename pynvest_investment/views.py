from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import datetime
import decimal


def current_year():
    return datetime.date.today().year

def investment(request, symbol):
    investment = get_object_or_404(models.Investment, symbol=symbol)

    return render_to_response('pynvest_investment/investment.html', {
        'title': investment.symbol,
        'investment': investment,
        'year': current_year(),
    })


def investment_snapshots(request, symbol, year):
    investment = get_object_or_404(models.Investment, symbol=symbol)
    year = int(year)

    vars = {
        'title': investment.symbol,
        'investment': investment,
        'snapshots': investment.snapshot_set.filter(date__year=year
                                           ).close_adjusted(
                                           ).order_by('-date'),
    }
    vars['prev_year'] = year - 1 if investment.snapshot_set.filter(date__year=(year-1)).exists() else None
    vars['next_year'] = year + 1 if year < current_year() else None
    return render_to_response('pynvest_investment/snapshots_table.html', vars)
