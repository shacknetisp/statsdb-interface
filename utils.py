# -*- coding: utf-8 -*-


def toint(v, d=0):
    try:
        return int(v)
    except:
        return d


def sliceneg(l, s):
    if s < 0:
        return l
    return l[:s]


def sok(d):
    if 'error' in d:
        return False
    return bool(d)


def version(s):
    return tuple([int(n) for n in s.split('.')])
