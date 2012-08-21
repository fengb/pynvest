from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import datetime
import decimal


def investment(request, symbol):
    investment = get_object_or_404(models.Investment, symbol=symbol)

    return render_to_response('pynvest_investment/investment.html', {
        'title': investment.symbol,
        'investment': investment,
    })


def investment_snapshots(request, symbol, year=None):
    investment = get_object_or_404(models.Investment, symbol=symbol)

    return render_to_response('pynvest_investment/snapshots_table.html', {
        'title': investment.symbol,
        'snapshots': investment.snapshot_set.filter(date__year=year
                                           ).close_adjusted(
                                           ).order_by('-date'),
    })
