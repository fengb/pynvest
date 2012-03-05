from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^portfolio/(?P<id>\d+)/$', views.portfolio),
    url(r'^portfolio/(?P<id>\d+)/(?P<year>\d+)/$', views.portfolio_summary_by_year),
    url(r'^portfolio/(?P<id>\d+)/(?P<year>\d+)/sales$', views.portfolio_sales_by_year),
    url(r'^portfolio/(?P<id>\d+)/flat/$', views.portfolio_flat),
)
