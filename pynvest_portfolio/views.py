from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters, util
import pynvest_core


def portfolio_summary(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    lots = models.Lot.objects.filter(portfolio=portfolio, outstanding_shares__gt=0)
    return render_to_response('pynvest_portfolio/lot_summary_table.html', {
        'title': portfolio.name,
        'lot_summarys': presenters.LotSummary.group_by_investment(lots),
    })


def portfolio_growth(request, id, compare=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)

    growths = [presenters.PortfolioGrowth(portfolio)]
    growths.append(growths[0].principal())
    if compare:
        for symbol in compare.split('+'):
            investment = get_object_or_404(pynvest_core.models.Investment, symbol=symbol)
            growths.append(growths[0].benchmark(investment))

    return render_to_response('pynvest_core/growths_table.html', {
        'title': portfolio.name,
        'growths': growths,
    })


def portfolio_sales(request, id, year):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.filter(lot__portfolio=portfolio, date__year=year)\
                                             .order_by('date', 'lot__investment')

    return render_to_response('pynvest_portfolio/transaction_sales_table.html', {
        'title': portfolio.name,
        'transactions': [t for t in transactions if t.base_transaction() != t],
    })


def portfolio_flat(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pynvest_portfolio/transactions.html', {
        'portfolio': portfolio,
        'transactions': models.Transaction.objects.filter(lot__portfolio=portfolio).order_by('date', 'lot__investment'),
    })
