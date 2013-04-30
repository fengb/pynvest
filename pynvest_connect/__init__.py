from . import cash, yahoo, google, morningstar


_MODULES = [yahoo, google, morningstar, cash]

def _invoke(funcname, *args, **kwargs):
    jurisdiction = kwargs.pop('jurisdiction', None)

    for module in _MODULES:
        if hasattr(module, funcname) and\
           (jurisdiction is None or jurisdiction in module.SUPPORTED_JURISDICTIONS):
            func = getattr(module, funcname)
            return func(*args, **kwargs)

    if jurisdiction:
        raise AttributeError('Cannot resolve "%s" for "%s"' % (funcname, jurisdiction))
    else:
        raise AttributeError('Cannot resolve "%s"' % funcname)


def historical_prices(*args, **kwargs):
    return _invoke('historical_prices', *args, **kwargs)

def adjusted_dividends(*args, **kwargs):
    return _invoke('adjusted_dividends', *args, **kwargs)

def splits(*args, **kwargs):
    return _invoke('splits', *args, **kwargs)

# FIXME: this should be non-adjusted
dividends = adjusted_dividends
