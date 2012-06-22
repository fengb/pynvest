from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^investment/(?P<symbol>\S+)/$', views.investment_historical_prices),
    url(r'^investment/(?P<symbol>\S+)/growth$', views.investment_growth),
)
