# -*- coding: utf-8 -*-
from . import base
from .base import tdlink
import dbselectors
import cgi
import timeutils
displays = {}


def server(sel):
    ret = ""
    ss = dbselectors.ServerSelector()
    ss.copyfrom(sel)
    server = ss.single(sel.pathid)
    if server is None:
        ret = "<div class='center'><h2>No such server.</h2></div>"
    else:
        recentgames = ""
        for gid, game in list(reversed(
            list(server["recentgames"].items())))[:10]:
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "#%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                dbselectors.modestr[game["mode"]])
            recentgames += tdlink('map', game["map"], game["map"])
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"] / 1000))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        server["desc"] = cgi.escape(server["desc"])
        ret += """
        <div class="center">
            <h2>{server[desc]}</h2>
            <h4>{server[handle]} [{server[flags]}]:
                Version {server[version]}</h4>
            <a href="redeclipse://{server[host]}:{server[port]}">
            {server[host]}:{server[port]}</a>
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Mode</th>
                        <th>Map</th>
                        <th>Duration</th>
                        <th>Played</th>
                    </tr>
                    {recentgames}
                </table>
            </div>
        </div>
        """.format(server=server, recentgames=recentgames)
    return base.page(sel, ret, title="Server %s" % sel.pathid)
displays["server"] = server