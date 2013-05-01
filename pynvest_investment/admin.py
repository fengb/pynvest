from django.contrib import admin
from . import models


admin.site.register([models.Jurisdiction, models.Investment])
