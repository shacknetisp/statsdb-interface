# -*- coding: utf-8 -*-
import cgi


def page(sel,
    content,
    title="-",
    css="",
    ):
        ret = open("web/base.html").read().format(
            content=content,
            title=title, css=css)
        return ret


def tdlink(t, i, d):
    return '<td><a href="/display/%s/%s">%s</a></td>' % (t, str(i),
        cgi.escape(str(d)))


def alink(t, i, d):
    return '<a href="/display/%s/%s">%s</a>' % (t, str(i),
        cgi.escape(str(d)))