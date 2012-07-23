from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^investment/(?P<symbol>\w+)/((?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})/)?$', views.investment_snapshots),
    url(r'^investment/(?P<symbol>\w+)/growth/$', views.investment_growth),
)
