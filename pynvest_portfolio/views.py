from django.shortcuts import render_to_response, get_object_or_404
from . import models, presenters
import pynvest_investment


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


def portfolio_sales(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.filter(lot__portfolio=portfolio
                                            ).order_by('date', 'lot__investment')
    if year:
        transactions = transactions.filter(date__year=year)

    return render_to_response('pynvest_portfolio/transaction_sales_table.html', {
        'title': portfolio.name,
        'transactions': [t for t in transactions if t.base_transaction() != t],
    })


def portfolio_transactions(request, id, year=None):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    transactions = models.Transaction.objects.raw('''SELECT MIN(t.id) as id, MIN(lot_id) as lot_id, date, price, SUM(shares) as shares
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
