from django.conf.urls import patterns, url


urlpatterns = patterns('pynvest_ownership.views',
    url(r'^(?P<portfolio_id>[^/]+)/owner/(?P<username>[^/]+)$', 'growth'),
)
