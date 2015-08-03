# -*- coding: utf-8 -*-
from . import base


def page(sel):
    ret = "<h2 class='center'>404 Error: Page not found.</h2>"
    return base.page(sel, ret, title="404")