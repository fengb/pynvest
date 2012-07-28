from django.db import models


class QuerySetManager(models.Manager):
    '''Allow for hassle-free QuerySet method extensions per model

    >>> class Entry(models.Model):
    ...     data = models.CharField()
    ...     objects = QuerySetManager()
    ...     class QuerySet(models.query.QuerySet):
    ...         def why(self):
    ...             return self.filter(data__like='y').order_by('data')

    >>> Entry.create(data='Philip')
    >>> Entry.create(data='Jay')
    >>> Entry.create(data='Fry')
    >>> [e.data for e in Entry.objects.why()]
    ['Jay', 'Fry']

    http://djangosnippets.org/snippets/734/'''

    use_for_related_fields = True

    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)
