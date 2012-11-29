from django.core.management.base import BaseCommand, CommandError
import pynvest_investment.batches


class Command(BaseCommand):
    help = 'Populates all prices for existing investments'

    def handle(self, *args, **options):
        pynvest_investment.batches.populate(output=self.stdout)
