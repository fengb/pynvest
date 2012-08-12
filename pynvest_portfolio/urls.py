from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/growth/$', views.portfolio_growth),
    url(r'^(?P<id>\d+)/compare/(?P<compare>[\w+]+)/$', views.portfolio_growth),
    url(r'^(?P<id>\d+)/(?P<year>\d+)/sales/$', views.portfolio_sales),
    url(r'^(?P<id>\d+)/flat/$', views.portfolio_flat),
)
