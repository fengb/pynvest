from django.conf.urls.defaults import patterns, url


def _generate(prefix, kwargs):
    def _generate_line(suffix, view):
        return url('^%s%s' % (prefix, suffix), view, kwargs=kwargs)

    return patterns('pynvest_portfolio.views',
        _generate_line(r'$',                             'summary'),
        _generate_line(r'growth/$',                      'growth'),
        _generate_line(r'compare/(?P<compare>[\w+]+)/$', 'growth'),
        _generate_line(r'sales/$',                       'sales'),
        _generate_line(r'sales/(?P<year>\d+)/$',         'sales'),
        _generate_line(r'transactions/$',                'transactions'),
        _generate_line(r'transactions/(?P<year>\d+)/$',  'transactions'),
        _generate_line(r'adjustments/$',                 'adjustments'),
        _generate_line(r'adjustments/(?P<year>\d+)/$',   'adjustments'),
    )


def portfolio(id):
    return _generate('', {'id': id})

urlpatterns = patterns('',
    url(r'^$', 'pynvest_portfolio.views.list'),
)

urlpatterns += _generate(r'(?P<id>\d+)/', {})
