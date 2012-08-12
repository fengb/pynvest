from . import yahoo, google, morningstar


class ApiNotFound(Exception): pass

_MODULES = {
  'yahoo': yahoo,
  'google': google,
  'morningstar': morningstar,
  '_default': yahoo,  # FIXME: replace Yahoo with a better public API
}

def module(kwargs):
    api = kwargs.pop('api', '_default')

    try:
        return _MODULES[api]
    except KeyError:
        raise ApiNotFound(api)


def historical_prices(*args, **kwargs):
    return module(kwargs).historical_prices(*args, **kwargs)


def dividends(*args, **kwargs):
    return module(kwargs).dividends(*args, **kwargs)
