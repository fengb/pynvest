from django.conf.urls.defaults import patterns, include, url
from . import views

urlpatterns = patterns('',
    url(r'^portfolio/(?P<id>\d+)/$', views.portfolio),
    url(r'^portfolio/(?P<id>\d+)/flat/$', views.portfolio_flat),
)
