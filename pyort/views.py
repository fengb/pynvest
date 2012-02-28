from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters

from . import util
import operator


def portfolio(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'title': portfolio.name,
        'transactions': presenters.TransactionAggregate.from_portfolio(portfolio).flatten(),
    })


def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(lot__portfolio=portfolio),
    })
