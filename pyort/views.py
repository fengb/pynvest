from django.shortcuts import render_to_response, get_object_or_404
from . import models


def portfolio(request, id):
    portfolio = get_object_or_404(models.Portfolio, id=id)
    return render_to_response('pyort/transaction_aggregates.html', {
        'portfolio': portfolio,
        'transaction_aggregates': [models.TransactionAggregate(basis.transaction_set.all())
                                     for basis in portfolio.basis_set.all()],
    })
