# -*- coding: utf-8 -*-
import cgi
import time


def page(sel,
    content,
    title="-",
    css="",
    ):
        db = ""
        if hasattr(sel, 'server'):
            db = """
            Time: %fs
            """.strip() % (time.time() - sel.server.starttime)
        ret = open("web/base.html").read().format(
            content=content,
            title=title, css=css, debuginfo=db)
        return ret


def tdlink(t, i, d, e=True):
    return '<td><a href="/%s/%s">%s</a></td>' % (t, str(i),
        cgi.escape(str(d)) if e else str(d))


def alink(t, i, d, e=True):
    return '<a href="/%s/%s">%s</a>' % (t, str(i),
        cgi.escape(str(d)) if e else str(d))


def tdlinkp(t, i, d, e=True):
    if not str(i):
        return '<td>%s</td>' % cgi.escape(str(d))
    return '<td><a href="/%s/%s">%s</a></td>' % (t, str(i),
        cgi.escape(str(d)) if e else str(d))


def alinkp(t, i, d, e=True):
    if not str(i):
        return '%s' % cgi.escape(str(d))
    return '<a href="/%s/%s">%s</a>' % (t, str(i),
        cgi.escape(str(d)) if e else str(d))