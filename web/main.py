# -*- coding: utf-8 -*-
from . import base
import api
import dbselectors
from .base import tdlink
from .base import alink
import timeutils


def page(sel):
    recentgames = ""
    gs = dbselectors.GameSelector()
    gs.copyfrom(sel)
    gs.pathid = None
    gs.qopt = api.Qopt({
        "recent": [True],
        })
    games = gs.getdict()
    for gid, game in list(reversed(list(games.items())))[:10]:
        recentgames += '<tr>'
        recentgames += tdlink("game", gid, "Game #%d" % gid)
        recentgames += tdlink("mode",
            game["mode"],
            dbselectors.modestr[game["mode"]])
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        desc = ss.single(game["server"])["desc"]
        recentgames += tdlink('server', game["server"], desc)
        recentgames += tdlink('map', game["map"], game["map"])
        recentgames += '<td>%s</td>' % timeutils.durstr(round(
            game["timeplayed"]))
        recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
        recentgames += '</tr>'
    players = {}
    for gid, game in list(reversed(list(games.items())))[:25]:
        if game["mode"] != 6:
            for player in game["players"]:
                if player["handle"]:
                    if player["handle"] not in players:
                        players[player["handle"]] = 0
                    players[player["handle"]] += player["score"]
    if players:
        best = sorted(list(players.items()), key=lambda x: -x[1])[0]
        topplayer = "<h3>Top player from recent games: %s [%d]</h3>" % (
            alink('player', best[0], best[0]), best[1])
    else:
        topplayer = ""

    ws = dbselectors.WeaponSelector()
    ws.copyfrom(sel)
    ws.pathid = None

    weapons = {}
    for name in dbselectors.loadoutweaponlist:
        weapon = ws.single(name)["recent"]
        weapons[name] = weapon

    topweapons = []
    if weapons:
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            weapon[1]["damage1"] / max(weapon[1]["timewielded"], 1) +
            weapon[1]["damage2"] / max(weapon[1]["timewielded"], 1)))[0]
        topweapons.append("<h3>Most efficient weapon: %s</h3>" % (
            alink('weapon', best[0], best[0])))
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            max(weapon[1]["timewielded"], 1)))[0]
        topweapons.append("<h3>Most wielded weapon: %s</h3>" % (
            alink('weapon', best[0], best[0])))
    ret = """
    <h2>Overview</h2>
    <div class='display-table'>
        {topplayer}
        {topweapon}
        <h3>Recent Games</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Mode</th>
                <th>Server</th>
                <th>Map</th>
                <th>Duration</th>
                <th>Played</th>
            </tr>
            {recentgames}
        </table>
    </div>
    """.format(recentgames=recentgames,
        topplayer=topplayer,
        topweapon="\n".join(topweapons))
    return base.page(sel, ret, title="Overview")
