from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters, util


def portfolio_summary(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    if year:
        transactions = models.Transaction.objects.filter(lot__portfolio=portfolio,
                                                         trade_date__year=int(year))
    else:
        transactions = models.Transaction.objects.filter(lot__portfolio=portfolio)
    return render_to_response('pyort/transaction_summary_table.html', {
        'title': portfolio.name,
        'transaction_summarys': presenters.TransactionSummary.group_by_lot(transactions),
    })


def portfolio_sales_by_year(request, id, year):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.filter(lot__portfolio=portfolio,
                                                     trade_date__year=int(year),
                                                     shares__lt=0)
    return render_to_response('pyort/transaction_sales_table.html', {
        'title': portfolio.name,
        'transaction_purchases_sales': [(t.lot.purchase_transaction(), t) for t in transactions],
    })


def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(lot__portfolio=portfolio),
    })
