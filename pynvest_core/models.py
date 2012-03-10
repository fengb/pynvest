from django.db import models


class Investment(models.Model):
    symbol          = models.CharField(max_length=5, unique=True)
    name            = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.symbol
