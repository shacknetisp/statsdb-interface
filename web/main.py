# -*- coding: utf-8 -*-
from . import base


def page(sel):
    ret = """
    <h2 class='center'>Red Eclipse Statistics</h2>
    <div class='center'>
    The main display is still in progress,
    however the <a href="/apidocs">JSON API</a> is working.
    </div>
    """
    return base.page(sel, ret, title="Overview")