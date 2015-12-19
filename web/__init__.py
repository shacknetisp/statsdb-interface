# -*- coding: utf-8 -*-


def page(content, title="", css="", debug=""):
    ret = open("files/html/base.html").read().format(
        content=content,
        title=(":" + title) if title else "", css=css, debuginfo=debug)
    return ret