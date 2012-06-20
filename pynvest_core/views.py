from django.shortcuts import render_to_response, get_object_or_404
from . import models


def historical_prices(request, symbol):
    investment = get_object_or_404(models.Investment, symbol=symbol)
    return render_to_response('pynvest_core/historical_prices_table.html', {
        'title': investment.symbol,
        'prices': investment.historicalprice_set.order_by('-date'),
    })
