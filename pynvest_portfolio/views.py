from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import pynvest_investment


def list(request):
    portfolios = models.Portfolio.objects.all()
    return render_to_response('pynvest_portfolio/list.html', {
        'title': 'Portfolios',
        'lot_summarys': [presenters.LotSummary(portfolio.lot_set.all()) for portfolio in portfolios],
    })

def summary(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    # FIXME: django<->sqlite3 bug https://code.djangoproject.com/ticket/18247
    #lots = [models.Lot.objects.filter(portfolio=portfolio).exclude(outstanding_shares=0)]
    lots = [l for l in models.Lot.objects.filter(portfolio=portfolio) if l.outstanding_shares != 0]
    return render_to_response('pynvest_portfolio/summary_table.html', {
        'title': portfolio.name,
        'lot_summarys': presenters.LotSummary.group_by_investment(lots),
    })


def growth(request, id, compare=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)

    growths = [presenters.PortfolioGrowth(portfolio)]
    if compare:
        for symbol in compare.split('+'):
            investment = get_object_or_404(pynvest_investment.models.Investment, symbol=symbol)
            growths.append(pynvest_investment.presenters.BenchmarkGrowth(growths[0], investment))
    else:
        growths.append(pynvest_investment.presenters.PrincipalGrowth(growths[0]))

    return render_to_response('pynvest_investment/growths_table.html', {
        'title': portfolio.name,
        'growths': growths,
    })


def sales(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.filter(lot__portfolio=portfolio, shares__lt=0
                                            ).order_by('date', 'lot__investment')
    if year:
        transactions = transactions.filter(date__year=year)

    return render_to_response('pynvest_portfolio/sales_table.html', {
        'title': portfolio.name,
        'transactions': transactions,
    })


def transactions(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.raw('''SELECT MIN(t.id) AS id, MIN(lot_id) AS lot_id, date, price, SUM(shares) AS shares
                                                       FROM pynvest_portfolio_transaction t
                                                       JOIN pynvest_portfolio_lot l
                                                         ON l.id = lot_id
                                                      WHERE portfolio_id = %s
                                                      GROUP BY date, price
                                                      ORDER BY date, investment_id
                                                  ''', [portfolio.id])

    return render_to_response('pynvest_portfolio/transactions.html', {
        'title': portfolio.name,
        'transactions': transactions,
    })


def adjustments(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    adjustments = models.Adjustment.objects.filter(portfolio=portfolio
                                          ).order_by('date', 'investment')
    if year:
        transactions = transactions.filter(date__year=year)

    return render_to_response('pynvest_portfolio/adjustments.html', {
        'title': portfolio.name,
        'adjustments': adjustments,
    })
