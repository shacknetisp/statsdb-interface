# -*- coding: utf-8 -*-
import time


def utcepoch():
    """Get the UTC epoch time."""
    return time.time()


def durstr(dur, skip="", dec=False):
    """Return dur as a formatted string."""
    ret = ""
    last = ""
    for style in [
        (60 * 60 * 24 * 365.25, 'Y'),
        (60 * 60 * 24 * 7, 'w'),
        (60 * 60 * 24, 'd'),
        (60 * 60, 'h'),
        (60, 'm'),
        (1, 's'),
        ]:
            if style[1] in skip:
                continue
            last = style[1]
            if not dec:
                amount = dur // style[0]
                extra = dur % style[0]
            else:
                amount = dur
            dur = extra
            if amount > 0:
                if round(amount) != amount and dec:
                    ret += '%.2f%s' % (amount, style[1])
                else:
                    ret += '%d%s' % (amount, style[1])

    return ret if ret else '0' + last


def agostr(ts, skip="", dec=False):
    """Return durstr(utcepoch() - ts)."""
    return durstr(utcepoch() - ts, skip, dec)


def agohtml(ts, skip="", ago=True):
    import datetime
    tss = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
    return "<abbr title='%s'>%s%s</abbr>" % (tss, agostr(ts, skip),
        " ago" if ago else "")