from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pynvest_investment.views',
    url(r'^(?P<symbol>[^/]+)/$',                       'summary'),
    url(r'^(?P<symbol>[^/]+)/price/(?P<year>\d{4})/$', 'snapshots'),
)
