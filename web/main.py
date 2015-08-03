# -*- coding: utf-8 -*-
from . import base
import api
import dbselectors


def page(sel):
    recentgames = ""
    gs = dbselectors.GameSelector()
    gs.copyfrom(sel)
    gs.qopt = api.Qopt({
        "recent": [True],
        })
    games = gs.getdict()
    for gid, game in list(reversed(list(games.items())))[:10]:
        recentgames += '<tr>'
        recentgames += '<td>#%d</td>' % gid
        recentgames += '<td>%s</td>' % dbselectors.modestr[game["mode"]]
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        desc = ss.single(game["server"])["desc"]
        recentgames += '<td>%s</td>' % desc
        recentgames += '<td>%s</td>' % game["map"]
        recentgames += '</tr>'
    ret = """
    <h2 class='center'>Red Eclipse Statistics</h2>
    <div class='center'>
    The main display is still in progress,
    however the <a href="/apidocs">JSON API</a> is working.
    </div>

    <div class='display-table'>
        <h3>Recent Games</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Mode</th>
                <th>Server</th>
                <th>Map</th>
            </tr>
            {recentgames}
        </table>
    </div>
    """.format(recentgames=recentgames)
    return base.page(sel, ret, title="Overview")