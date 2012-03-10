from django.contrib import admin
from . import models


admin.site.register([models.Investment, models.Portfolio, models.Lot, models.Transaction])
