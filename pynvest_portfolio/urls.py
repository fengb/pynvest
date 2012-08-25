from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('pynvest_portfolio.views',
    url(r'^(?P<id>\d+)/$',                             'portfolio_summary'),
    url(r'^(?P<id>\d+)/growth/$',                      'portfolio_growth'),
    url(r'^(?P<id>\d+)/compare/(?P<compare>[\w+]+)/$', 'portfolio_growth'),
    url(r'^(?P<id>\d+)/sales/$',                       'portfolio_sales'),
    url(r'^(?P<id>\d+)/sales/(?P<year>\d+)/$',         'portfolio_sales'),
    url(r'^(?P<id>\d+)/transactions/$',                'portfolio_transactions'),
    url(r'^(?P<id>\d+)/transactions/(?P<year>\d+)/$',  'portfolio_transactions'),
)
