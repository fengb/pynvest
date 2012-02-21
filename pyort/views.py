from django.shortcuts import render_to_response, get_object_or_404
from . import models

import collections


def _render_transactions_grouped(transactions_grouped, portfolio=None):
    return render_to_response('pyort/transaction_aggregates.html', {
        'portfolio': portfolio,
        'transaction_aggregates': map(models.TransactionAggregate, transactions_grouped),
    })


def portfolio(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)

    transactions_by_investment = collections.defaultdict(list)
    for transaction in models.Transaction.objects.filter(lot__portfolio=portfolio):
        investment = transaction.lot.investment
        transactions_by_investment[investment].append(transaction)

    return _render_transactions_grouped(transactions_by_investment.values())


def portfolio_lot(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return _render_transactions_grouped(lot.transaction_set.all()
                                          for lot in portfolio.lot_set.all())


