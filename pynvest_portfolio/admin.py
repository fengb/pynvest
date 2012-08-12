from django.contrib import admin
from . import models


admin.site.register([models.Portfolio, models.Adjustment, models.Lot, models.Transaction])
