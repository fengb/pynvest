from django.shortcuts import render_to_response, get_object_or_404
from . import models

from . import util
import operator


def portfolio(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'title': portfolio.name,
        'transactions': models.TransactionAggregate.for_portfolio_by_investment(portfolio),
    })


def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(lot__portfolio=portfolio)
    })
