def groupbyrollup(iter, key):
    '''Like itertools.groupby but rolls up everything, not just sorted values'''
    rollup = {}
    rkeys = []
    for rval in iter:
        rkey = key(rval)
        if rkey not in rkeys:
            rkeys.append(rkey)
            rollup[rkey] = []
        rollup[rkey].append(rval)
    return ((k, rollup[k]) for k in rkeys)
