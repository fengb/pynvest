from django.db import models


class AnnotatedLotManager(models.Manager):
    '''TODO: remove tight coupling with Lot'''

    use_for_related_fields = True

    def get_query_set(self):
        objects = super(AnnotatedLotManager, self).get_query_set()
        return objects.annotate(outstanding_shares=models.Sum('transaction__shares'))
