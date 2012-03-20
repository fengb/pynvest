from django.contrib import admin
from . import models


admin.site.register([models.Portfolio, models.Lot, models.Transaction, models.LotTransaction])
