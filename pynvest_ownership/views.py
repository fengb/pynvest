from django.shortcuts import render_to_response, get_object_or_404
from . import models
import pynvest_portfolio


def growth(request, portfolio_id, username):
    portfolio = get_object_or_404(pynvest_portfolio.models.Portfolio, id=portfolio_id)
    user = get_object_or_404(models.User, username=username)
    growth = models.Growth(portfolio, user)

    return render_to_response('pynvest_investment/growths_table.html', {
        'title': portfolio.name,
        'growths': [growth],
    })
