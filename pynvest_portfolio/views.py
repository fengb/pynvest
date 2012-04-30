from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters, util


def portfolio_summary(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.filter(portfolio=portfolio)
    return render_to_response('pyort/transaction_summary_table.html', {
        'title': portfolio.name,
        'transaction_summarys': presenters.TransactionSummary.group_by_investment(transactions),
    })


def portfolio_sales(request, id, year):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.LotTransaction.objects.filter(transaction__portfolio=portfolio,
                                                        transaction__date__year=year)

    return render_to_response('pyort/transaction_sales_table.html', {
        'title': portfolio.name,
        'transactions': [t for t in transactions if t.origin() != t],
    })


def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(portfolio=portfolio),
    })
