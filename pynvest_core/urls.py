from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<symbol>\S+)/$', views.historical_prices),
)
