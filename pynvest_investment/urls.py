from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<symbol>\w+)/$', views.investment, name='investment'),
    url(r'^(?P<symbol>\w+)/price/(?P<year>\d{4})/$', views.investment_snapshots, name='investment_snapshots'),
)
