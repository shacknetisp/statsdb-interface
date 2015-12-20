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
