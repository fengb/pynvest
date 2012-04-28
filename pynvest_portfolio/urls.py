from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^(?P<id>\d+)/$', views.portfolio_summary),
    url(r'^(?P<id>\d+)/flat/$', views.portfolio_flat),
)
