from django.contrib import admin
from . import models


admin.site.register([models.Portfolio, models.Dividend, models.Lot, models.Transaction])
