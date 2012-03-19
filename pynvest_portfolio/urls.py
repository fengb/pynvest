from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/lot/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/lot/(?P<year>\d+)/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/flat/$', views.portfolio_flat),
)
