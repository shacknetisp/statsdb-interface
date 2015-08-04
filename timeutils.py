# -*- coding: utf-8 -*-


def utcepoch():
    """Get the UTC epoch time."""
    import datetime
    dt = datetime.datetime.utcnow()
    return dt.timestamp()


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
            amount = dur // style[0]
            extra = dur % style[0]
            if dec and style[0] == 1:
                amount = dur
            dur = extra
            if amount > 0:
                if round(amount) != amount and dec:
                    ret += '%.3f%s' % (amount, style[1])
                else:
                    ret += '%d%s' % (amount, style[1])

    return ret if ret else '0' + last


def agostr(ts, skip="", dec=False):
    import time
    return durstr(time.time() - ts, skip, dec)


def agohtml(ts, skip="", ago=True):
    import time
    tss = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))
    return "<abbr title='%s'>%s%s</abbr>" % (tss, agostr(ts, skip),
        " ago" if ago else "")