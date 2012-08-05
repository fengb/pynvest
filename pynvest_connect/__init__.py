from . import yahoo, google, morningstar


class ApiNotFound(Exception): pass

_MODULES = {
  'yahoo': yahoo,
  'google': google,
  'morningstar': morningstar,
  '_default': yahoo,  # FIXME: replace with a better public API
}


def historical_prices(*args, **kwargs):
    api = kwargs.get('api', '_default')

    try:
        module = _MODULES[api]
    except KeyError:
        raise ApiNotFound(api)
    else:
        return module.historical_prices(*args)
