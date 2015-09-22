# -*- coding: utf-8 -*-
from . import base
import api
import dbselectors
import redeclipse
from .base import tdlink
from .base import alink
import timeutils
import time


class pt:

    def game(key, sel):
        ret = ""
        players = {}
        for gid in [x[0] for x in sel.db.con.execute("""
        SELECT id FROM games WHERE (%d - time) < (60 * 60 * 24 * 90)
        """ % time.time())]:
            game = dbselectors.GameSelector(sel).single(gid)
            if game["mode"] != redeclipse.modes["race"]:
                for player in game["players"]:
                    if player["handle"]:
                        if player["handle"] not in players:
                            players[player["handle"]] = 0
                        players[player["handle"]] += key(player)
        for player in sorted(list(players.items()), key=lambda x: -x[1])[:5]:
            ret += "<tr>"
            ret += tdlink("player", player[0], player[0])
            ret += "<td>%d</td>" % player[1]
            ret += "</tr>"
        return ret

    def gamediv(key, akey, sel):
        ret = ""
        players = {}
        d = {}
        for gid in [x[0] for x in sel.db.con.execute("""
        SELECT id FROM games WHERE (%d - time) < (60 * 60 * 24 * 90)
        """ % time.time())]:
            game = dbselectors.GameSelector(sel).single(gid)
            if game["mode"] != redeclipse.modes["race"]:
                for player in game["players"]:
                    if player["handle"]:
                        if player["handle"] not in players:
                            players[player["handle"]] = 0
                        players[player["handle"]] += key(player)
                        if player["handle"] not in d:
                            d[player["handle"]] = 0
                        d[player["handle"]] += akey(player)
        for player in sorted(list(players.items()), key=lambda x: -x[1])[:5]:
            ret += "<tr>"
            ret += tdlink("player", player[0], player[0])
            ret += "<td>%d</td>" % round(player[1] / d[player[0]])
            ret += "</tr>"
        return ret

    def mapnum(sel):
        ret = ""
        ms = {}
        for gid in [x[0] for x in sel.db.con.execute("""
            SELECT id FROM games WHERE (%d - time) < (60 * 60 * 24 * 90)
            """ % time.time())]:
                game = dbselectors.GameSelector(sel).single(gid)
                if game["map"] not in ms:
                    ms[game["map"]] = 0
                ms[game["map"]] += 1
        for m in sorted(ms, key=lambda x: -ms[x])[:5]:
            ret += "<tr>"
            ret += tdlink("map", m, m)
            ret += "<td>%d</td>" % (ms[m])
            ret += "</tr>"
        return ret


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
            redeclipse.modestr[game["mode"]])
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        desc = ss.single(game["server"])["desc"]
        recentgames += tdlink('server', game["server"], desc)
        recentgames += tdlink('map', game["map"], game["map"])
        recentgames += '<td>%s</td>' % timeutils.durstr(round(
            game["timeplayed"]))
        recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
        recentgames += '</tr>'

    ws = dbselectors.WeaponSelector()
    ws.copyfrom(sel)
    ws.pathid = None

    weapons = {}
    for name in redeclipse.loadoutweaponlist:
        weapon = ws.single(name)["recent"]
        weapons[name] = weapon

    topweapons = []
    if weapons:
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            weapon[1]["damage1"] / max(weapon[1]["timewielded"], 1) +
            weapon[1]["damage2"] / max(weapon[1]["timewielded"], 1)))[0]
        topweapons.append("Most efficient weapon: %s<br>" % (
            alink('weapon', best[0], best[0])))
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            max(weapon[1]["timewielded"], 1)))[0]
        topweapons.append("Most wielded weapon: %s<br>" % (
            alink('weapon', best[0], best[0])))

    ptcounters = {
        "points": pt.game(lambda x: x["score"], sel),
        "captures": pt.game(lambda x: len(x["captures"]), sel),
        "bombings": pt.game(lambda x: len(x["bombings"]), sel),
        "dpm": pt.gamediv(lambda x: x["damage"],
            lambda x: x["timealive"] / 60, sel),
        "maps": pt.mapnum(sel),
        }
    ret = """
    <h2>Recent Overview</h2>
    <h3>Last 90 Days</h3>
    <h5>Players</h5>
    <div class='display-table float-table'>
        <h5>DPM</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>DPM</th>
            </tr>
            {ptcounters[dpm]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5>Points</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Points</th>
            </tr>
            {ptcounters[points]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5>Captures</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Captures</th>
            </tr>
            {ptcounters[captures]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5>Bombings</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Bombings</th>
            </tr>
            {ptcounters[bombings]}
        </table>
    </div>
    <div style="clear: both;"></div>
    <div class='display-table float-table'>
        <h5>Maps</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Games</th>
            </tr>
            {ptcounters[maps]}
        </table>
    </div>
    <div style="clear: both;"></div>
    <div class='display-table'>
        <h5>Latest Games</h5>
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
    <div style="clear: both;"></div>
    """.format(recentgames=recentgames,
        ptcounters=ptcounters,
        topweapon="\n".join(topweapons))
    return base.page(sel, ret, title="Overview")
