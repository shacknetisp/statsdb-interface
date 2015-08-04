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
    return '<td><a href="/display/%s/%s">%s</td>' % (t, str(i),
        cgi.escape(str(d)))