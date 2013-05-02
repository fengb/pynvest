from django.conf.urls.defaults import patterns, include, url


def portfolio(id):
    return patterns('pynvest_portfolio.views',
        url(r'^$',                             'summary', kwargs={'id': id}),
        url(r'^growth/$',                      'growth', kwargs={'id': id}),
        url(r'^compare/(?P<compare>[\w+]+)/$', 'growth', kwargs={'id': id}),
        url(r'^sales/$',                       'sales', kwargs={'id': id}),
        url(r'^sales/(?P<year>\d+)/$',         'sales', kwargs={'id': id}),
        url(r'^transactions/$',                'transactions', kwargs={'id': id}),
        url(r'^transactions/(?P<year>\d+)/$',  'transactions', kwargs={'id': id}),
        url(r'^adjustments/$',                 'adjustments', kwargs={'id': id}),
        url(r'^adjustments/(?P<year>\d+)/$',   'adjustments', kwargs={'id': id}),
    )

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
