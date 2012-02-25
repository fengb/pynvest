from django.shortcuts import render_to_response, get_object_or_404
from . import models

from . import util
import operator


def _render_transactions_grouped(transactions_grouped, portfolio=None):
    return render_to_response('pyort/transaction_aggregates.html', {
        'portfolio': portfolio,
        'transaction_aggregates': [models.TransactionAggregate(v)
                                    for (k, v) in transactions_grouped],
    })


def portfolio(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)

    transactions = models.Transaction.objects.filter(lot__portfolio=portfolio)
    grouped = util.groupbyrollup(transactions, key=operator.attrgetter('investment'))

    return _render_transactions_grouped(grouped)


def portfolio_lot(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return _render_transactions_grouped((lot, lot.transaction_set.all())
                                          for lot in portfolio.lot_set.all())

def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(lot__portfolio=portfolio)
    })
