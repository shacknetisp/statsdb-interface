# -*- coding: utf-8 -*-


def utcepoch():
    """Get the UTC epoch time."""
    import datetime
    dt = datetime.datetime.utcnow()
    return dt.timestamp()


def durstr(dur, skip="", dec=False, full=False, skiplow=True):
    """Return dur as a formatted string."""
    firstdur = dur
    ret = ""
    last = (1, "")
    for style in [
        (60 * 60 * 24 * 365.25, 'Y', 0),
        (60 * 60 * 24 * 7, 'w', 52 * 2),
        (60 * 60 * 24, 'd', 7),
        (60 * 60, 'h', 24),
        (60, 'm', 60),
        (1, 's', 60),
        ]:
            if style[1] in skip:
                continue
            if full:
                style = (style[0], style[1].strip() + (' ' if full else ''),
                    style[2])
            last = style
            amount = dur // style[0]
            extra = dur % style[0]
            if (style[2] and firstdur / style[0] > style[2]
                and not dec and skiplow):
                break
            if dec and style[0] == 1:
                amount = dur
            dur = extra
            if amount > 0:
                if round(amount) != amount and dec:
                    ret += '%.3f%s' % (amount, style[1])
                else:
                    ret += '%d%s' % (amount, style[1])

    return ret if ret else '0' + last[1]


def agostr(ts, skip="", dec=False):
    import time
    return durstr(time.time() - ts, skip, dec)


def agohtml(ts, skip="", ago=True):
    import time
    tss = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))
    return "<span class='ago-title' title='%s'>%s%s</span>" % (
        tss, agostr(ts, skip),
        " ago" if ago else "")