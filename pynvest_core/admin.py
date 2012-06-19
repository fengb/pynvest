from django.contrib import admin
from . import models


admin.site.register([models.Exchange, models.Investment])
