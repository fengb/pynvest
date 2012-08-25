from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pynvest_investment.views',
    url(r'^(?P<symbol>\w+)/$',                       'investment'),
    url(r'^(?P<symbol>\w+)/price/(?P<year>\d{4})/$', 'investment_snapshots'),
)
