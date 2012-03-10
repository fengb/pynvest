from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.portfolio),
    url(r'^(?P<id>\d+)/lot/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/lot/(?P<year>\d+)/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/(?P<year>\d+)/sales$', views.portfolio_sales_by_year),
    url(r'^(?P<id>\d+)/flat/$', views.portfolio_flat),
)
