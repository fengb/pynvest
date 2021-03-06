from django.conf.urls import patterns, include, url

import pynvest_portfolio

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pynvest.views.home', name='home'),
    # url(r'^pynvest/', include('pynvest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^investment/', include('pynvest_investment.urls')),
    url(r'^portfolio/', include('pynvest_portfolio.urls')),
    url(r'^p1/', include(pynvest_portfolio.urls.portfolio(1))),
    url(r'^portfolio/', include('pynvest_ownership.urls')),
)
