# -*- coding: utf-8 -*-
from . import base


def page(sel):
    ret = "<h2 class='center'>The server has encountered an error.</h2>"
    return base.page(sel, ret, title="500 Internal Server Error")