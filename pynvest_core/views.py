from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import decimal


def _investment(symbol):
    try:
        return models.Investment.objects.get(symbol=symbol)
    except models.Investment.DoesNotExist:
        models.HistoricalPriceMeta.populate(symbol)
        return get_object_or_404(Investment, symbol=symbol)

def investment_historical_prices(request, symbol):
    investment = _investment(symbol)

    return render_to_response('pynvest_core/historical_prices_table.html', {
        'title': investment.symbol,
        'prices': investment.historicalprice_set.order_by('-date'),
    })


def investment_growth(request, symbol):
    investment = _investment(symbol)

    return render_to_response('pynvest_core/growth_table.html', {
        'title': investment.symbol,
        'growth': presenters.InvestmentGrowth.lump_sum(investment, start_value=decimal.Decimal(10000))
    })
