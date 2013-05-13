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

    There is a hook 'from_manager' that will be called after the standard
    constructor if it exists.  This will automatically run whenever
    get_query_set() is called.

    >>> class Entry(models.Model):
    ...     data = models.CharField()
    ...     objects = QuerySetManager()
    ...     class QuerySet(models.query.QuerySet):
    ...         def from_manager(self):
    ...             return self.filter(data__like='y').order_by('data')

    >>> Entry.create(data='Philip')
    >>> Entry.create(data='Jay')
    >>> Entry.create(data='Fry')
    >>> [e.data for e in Entry.objects.all()]
    ['Jay', 'Fry']

    http://djangosnippets.org/snippets/734/'''

    use_for_related_fields = True

    def get_query_set(self):
        ret = self.model.QuerySet(self.model)
        if hasattr(ret, 'from_manager'):
            ret = ret.from_manager()
        return ret

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)
