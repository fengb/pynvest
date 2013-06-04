import django
from pynvest_ownership import models
import pynvest_portfolio.presenters


class Command(django.core.management.base.BaseCommand):
    help = 'Create unit contributions'

    def handle(self, *args, **options):
        portfolios = pynvest_portfolio.models.Portfolio.objects.all()
        for portfolio in portfolios:
            growth = portfolio.growth()
            contributions = models.Contribution.objects.filter(transaction__lot__portfolio=portfolio)\
                                                       .order_by('transaction__date')

            with django.db.transaction.commit_on_success():
                total_units = 0
                for contribution in contributions:
                    if hasattr(contribution, 'unitcontribution'):
                        total_units += contribution.unitcontribution.units
                        continue

                    if total_units == 0:
                        units = contribution.amount()
                    else:
                        units = contribution.amount() * total_units / (growth[contribution.date] - contribution.amount())

                    models.UnitContribution.objects.create(contribution=contribution,
                                                           units=units)
                    total_units += units
