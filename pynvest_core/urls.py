from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^investment/(?P<symbol>\S+)/$', views.investment_snapshots),
    url(r'^investment/(?P<symbol>\S+)/growth$', views.investment_growth),
)
