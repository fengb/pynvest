from . import yahoo, google, morningstar


_MODULES = [yahoo, google, morningstar]

def _invoke(funcname, *args, **kwargs):
    for module in _MODULES:
        if hasattr(module, funcname):
            func = getattr(module, funcname)
            return func(*args, **kwargs)

    raise AttributeError('Cannot resolve "%s"' % funcname)


def historical_prices(*args, **kwargs):
    return _invoke('historical_prices', *args, **kwargs)

def adjusted_dividends(*args, **kwargs):
    return _invoke('adjusted_dividends', *args, **kwargs)

def splits(*args, **kwargs):
    return _invoke('splits', *args, **kwargs)

# FIXME: this should be non-adjusted
dividends = adjusted_dividends
