from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pynvest_portfolio.views',
    url(r'^$',                                         'list'),
    url(r'^(?P<id>\d+)/$',                             'summary'),
    url(r'^(?P<id>\d+)/growth/$',                      'growth'),
    url(r'^(?P<id>\d+)/compare/(?P<compare>[\w+]+)/$', 'growth'),
    url(r'^(?P<id>\d+)/sales/$',                       'sales'),
    url(r'^(?P<id>\d+)/sales/(?P<year>\d+)/$',         'sales'),
    url(r'^(?P<id>\d+)/transactions/$',                'transactions'),
    url(r'^(?P<id>\d+)/transactions/(?P<year>\d+)/$',  'transactions'),
    url(r'^(?P<id>\d+)/adjustments/$',                 'adjustments'),
    url(r'^(?P<id>\d+)/adjustments/(?P<year>\d+)/$',   'adjustments'),
)
