from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pynvest_investment.views',
    url(r'^(?P<symbol>\w+)/$',                       'summary'),
    url(r'^(?P<symbol>\w+)/price/(?P<year>\d{4})/$', 'snapshots'),
)
