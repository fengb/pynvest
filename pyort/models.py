from django.db import models


class Investment(models.Model):
    symbol          = models.CharField(max_length=5, unique=True)
    name            = models.CharField(max_length=200)


class Snapshot(models.Model):
    investment      = models.ForeignKey(Investment)
    date            = models.DateField()
    price           = models.DecimalField(max_digits=12, decimal_places=4)


class Portfolio(models.Model):
    name            = models.CharField(max_length=200)


class Holding(models.Model):
    portfolio       = models.ForeignKey(Portfolio)
    snapshot        = models.ForeignKey(Snapshot)

    shares          = models.DecimalField(max_digits=15, decimal_places=4)
