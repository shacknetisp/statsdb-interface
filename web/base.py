# -*- coding: utf-8 -*-


def page(sel,
    content,
    title="-",
    css="",
    ):
        ret = open("web/base.html").read().format(
            content=content,
            title=title, css=css)
        return ret