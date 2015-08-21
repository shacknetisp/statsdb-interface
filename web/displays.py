# -*- coding: utf-8 -*-
from . import base
from .base import tdlink, alink, tdlinkp, alinkp
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
        for gid, game in sorted(list(server["recentgames"].items()),
            key=lambda x: -x[0])[:10]:
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                dbselectors.modestr[game["mode"]])
            recentgames += tdlink('map', game["map"], game["map"])
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"]))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        server["desc"] = cgi.escape(server["desc"])
        ret += """
        <div class="center">
            <h2>{server[desc]}</h2>
            <h4>{server[handle]} [{server[flags]}]:
                Version {server[version]}</h4>
            <a href="redeclipse://{server[host]}:{server[port]}">
            {server[host]}:{server[port]}</a><br>
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


def game(sel):
    ret = ""
    gs = dbselectors.GameSelector()
    gs.copyfrom(sel)
    game = gs.single(sel.pathid)
    if game is None:
        ret = "<div class='center'><h2>No such game.</h2></div>"
    else:
        game["map"] = cgi.escape(game["map"])
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        server = ss.single(game["server"])
        server["desc"] = cgi.escape(server["desc"])
        teamsstr = ""
        for team in game["teams"]:
            team = game["teams"][team]
            teamsstr += "<tr>"
            teamsstr += "<td>%s</td>" % cgi.escape(team["name"])
            teamsstr += "<td>%s</td>" % (dbselectors.scorestr(game,
                team["score"]))
            teamsstr += "</tr>"
        playersstr = ""
        for player in game["players"]:
            playersstr += "<tr>"
            playersstr += tdlinkp("player", player["handle"], player["name"])
            playersstr += "<td>%s</td>" % (dbselectors.scorestr(game,
                player["score"]))
            playersstr += tdlinkp("player", player["handle"], player["handle"])
            playersstr += "<td>%s</td>" % (
                timeutils.durstr(player["timealive"]))
            playersstr += "<td>%d</td>" % player["frags"]
            playersstr += "<td>%d</td>" % player["deaths"]
            playersstr += "</tr>"
        ret += """
        <div class="center">
            <h2>Game #{game[id]}: {modestr} on {mapstr}</h2>
            Duration: {duration}<br>
            Played: {agohtml}<br>
            Server: <a
            href="/display/server/{server[handle]}">{server[desc]}</a><br>
            <div class='display-table'>
                <h3>Teams</h3>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Score</th>
                    </tr>
                    {teams}
                </table>
            </div>
            <div class='display-table'>
                <h3>Players</h3>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Score</th>
                        <th>Handle</th>
                        <th>Alive</th>
                        <th>Frags</th>
                        <th>Deaths</th>
                    </tr>
                    {players}
                </table>
            </div>
        </div>
        """.format(
            modestr=alink("mode", game["mode"],
                dbselectors.modestr[game["mode"]]),
            mapstr=alink("map", game["map"], game["map"]),
            agohtml=timeutils.agohtml(game["time"]),
            duration=timeutils.durstr(game["timeplayed"]),
            game=game, server=server, teams=teamsstr, players=playersstr)
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["game"] = game


def player(sel):
    ret = ""
    gs = dbselectors.PlayerSelector()
    gs.copyfrom(sel)
    player = gs.single(sel.pathid)
    if player is None:
        ret = "<div class='center'><h2>No such player.</h2></div>"
    else:
        player["name"] = cgi.escape(player["name"])
        recentgames = ""
        for gid, game in sorted(list(player["recentgames"].items()),
            key=lambda x: -x[0])[:10]:
                entry = [p for p in game["players"]
                if p["handle"] == player["handle"]][0]
                recentgames += '<tr>'
                recentgames += tdlink("game", gid,
                    "#%d (%s on %s)" % (gid, dbselectors.modestr[game["mode"]],
                        game["map"]))
                recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
                recentgames += '<td>%s</td>' % cgi.escape(entry["name"])
                recentgames += '<td>%s</td>' % dbselectors.scorestr(game,
                    entry["score"])
                recentgames += '<td>%d</td>' % entry["frags"]
                recentgames += '<td>%d</td>' % entry["deaths"]
                recentgames += '</tr>'
        recentweapons = ""
        try:
            fratio = "%.2f" % (player["recent"]["frags"] /
                max(1, player["recent"]["deaths"]))
        except TypeError:
            fratio = "-"
        try:
            totalwielded = sum([w['timewielded']
                for w in list(player['recent']['weapons'].values())])
            for weap in sorted(dbselectors.weaponlist):
                weapon = player['recent']['weapons'][weap]
                recentweapons += "<tr>"
                recentweapons += "%s" % tdlink("weapon", weap, weap)
                recentweapons += "<td>%d%%</td>" % (
                    weapon["timeloadout"] / max(1, totalwielded) * 100)
                recentweapons += "<td>%d%%</td>" % (
                    weapon["timewielded"] / max(1, totalwielded) * 100)
                recentweapons += "<td>%d%%</td>" % (
                    weapon["hits1"] / max(1, weapon["shots1"]) * 100)
                recentweapons += "<td>%d%%</td>" % (
                    weapon["hits2"] / max(1, weapon["shots2"]) * 100)
                recentweapons += "<td>%d</td>" % weapon["frags1"]
                recentweapons += "<td>%d</td>" % weapon["frags2"]
                recentweapons += "</tr>"
        except TypeError:
            pass
        gs = dbselectors.GameSelector()
        gs.copyfrom(sel)
        firstago = '<a href="/display/game/%d">%s</a>' % (min(player["games"]),
            timeutils.agohtml(gs.single(min(player["games"]))["time"]))
        lastago = '<a href="/display/game/%d">%s</a>' % (max(player["games"]),
            timeutils.agohtml(gs.single(max(player["games"]))["time"]))
        ret += """
        <div class="center">
            <h2>{player[name]}</h2>
            <h3>{player[handle]}</h3>
            First appeared: {firstago}<br>
            Last appeared: {lastago}<br>
            Frag Ratio: {fratio}<br>
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>Game</th>
                        <th>Time</th>
                        <th>Played As</th>
                        <th>Score</th>
                        <th>Frags</th>
                        <th>Deaths</th>
                    </tr>
                    {recentgames}
                </table>
            </div>
            <div class='display-table'>
                <h3>Weapon Statistics</h3>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Loadout</th>
                        <th>Wielded</th>
                        <th>Hit Ratio 1</th>
                        <th>Hit Ratio 2</th>
                        <th>Frags 1</th>
                        <th>Frags 2</th>
                    </tr>
                    {recentweapons}
                </table>
            </div>
        </div>
        """.format(recentgames=recentgames,
            player=player, firstago=firstago, lastago=lastago,
            fratio=fratio,
            recentweapons=recentweapons)
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["player"] = player


def weapon_disp(sel):
    ret = ""
    gs = dbselectors.WeaponSelector()
    gs.copyfrom(sel)
    gs.pathid = None
    totalwielded = sum([w['alltime']['timewielded']
        for w in list(gs.getdict().values())])
    weapon = gs.single(sel.pathid)["alltime"]
    if weapon is None or sel.pathid not in dbselectors.weaponlist:
        ret = "<div class='center'><h2>No such weapon.</h2></div>"
    else:
        weapon["name"] = cgi.escape(sel.pathid)
        weapons = ""
        try:
            weapons += "<tr>"
            weapons += "<td>%s</td>" % cgi.escape(weapon["name"])
            weapons += "<td>%d%%</td>" % (
                weapon["timeloadout"] / max(1, totalwielded) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["timewielded"] / max(1, totalwielded) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["hits1"] / max(1, weapon["shots1"]) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["hits2"] / max(1, weapon["shots2"]) * 100)
            weapons += "<td>%d</td>" % weapon["frags1"]
            weapons += "<td>%d</td>" % weapon["frags2"]
            weapons += "</tr>"
        except TypeError:
            pass
        ret += """
        <div class="center">
            <h2>{weapon[name]}</h2>
            <div class='display-table'>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Loadout</th>
                        <th>Wielded</th>
                        <th>Hit Ratio 1</th>
                        <th>Hit Ratio 2</th>
                        <th>Frags 1</th>
                        <th>Frags 2</th>
                    </tr>
                    {weapons}
                </table>
            </div>
        </div>
        """.format(weapon=weapon, weapons=weapons)
    try:
        return base.page(sel, ret, title="%s" % sel.pathid.capitalize())
    except AttributeError:
        return base.page(sel, ret)
displays["weapon"] = weapon_disp


def weapons(sel):
    if sel.pathid:
        return weapon_disp(sel)
    ret = ""
    gs = dbselectors.WeaponSelector()
    gs.copyfrom(sel)
    gs.pathid = None
    weapons = ""
    totalwielded = sum([w['alltime']['timewielded']
        for w in list(gs.getdict().values())])
    for name in sorted(dbselectors.weaponlist):
        weapon = gs.single(name)["alltime"]
        weapon["name"] = cgi.escape(name)
        weap = weapon["name"]
        try:
            weapons += "<tr>"
            weapons += "%s" % tdlink("weapon", weap, weap)
            weapons += "<td>%d%%</td>" % (
                weapon["timeloadout"] / max(1, totalwielded) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["timewielded"] / max(1, totalwielded) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["hits1"] / max(1, weapon["shots1"]) * 100)
            weapons += "<td>%d%%</td>" % (
                weapon["hits2"] / max(1, weapon["shots2"]) * 100)
            weapons += "<td>%d</td>" % weapon["frags1"]
            weapons += "<td>%d</td>" % weapon["frags2"]
            weapons += "</tr>"
        except TypeError:
            pass
    ret += """
    <div class="center">
        <h2>Weapons</h2>
        <div class='display-table'>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Loadout</th>
                    <th>Wielded</th>
                    <th>Hit Ratio 1</th>
                    <th>Hit Ratio 2</th>
                    <th>Frags 1</th>
                    <th>Frags 2</th>
                </tr>
                {weapons}
            </table>
        </div>
    </div>
    """.format(weapons=weapons)
    return base.page(sel, ret, title="Weapons")
displays["weapons"] = weapons


def map(sel):
    ret = ""
    gs = dbselectors.MapSelector()
    gs.copyfrom(sel)
    gamemap = gs.single(sel.pathid)
    if gamemap is None:
        ret = "<div class='center'><h2>No such Map.</h2></div>"
    else:
        recentgames = ""
        for gid, game in sorted(list(gamemap["recentgames"].items()),
            key=lambda x: -x[0])[:10]:
                recentgames += '<tr>'
                recentgames += tdlink("game", gid, "Game #%d" % gid)
                recentgames += tdlink("mode",
                    game["mode"],
                    dbselectors.modestr[game["mode"]])
                recentgames += '<td>%s</td>' % timeutils.durstr(round(
                    game["timeplayed"]))
                recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
                recentgames += '</tr>'
        toprace = ""
        if gamemap["toprace"]["time"]:
            toprace = """<h3>%s by %s (%s)</h3>""" % (
                timeutils.durstr(gamemap["toprace"]["time"] / 1000, dec=True),
                alinkp("player", gamemap["toprace"]["gameplayer"]["handle"],
                    gamemap["toprace"]["gameplayer"]["name"]),
                alink("game", gamemap["toprace"]["game"]["id"],
                    "Game #%d" % gamemap["toprace"]["game"]["id"]),
                )
        ret += """
        <div class="center">
            <h2>{map[name]}</h2>
            {toprace}
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Mode</th>
                        <th>Duration</th>
                        <th>Played</th>
                    </tr>
                    {recentgames}
                </table>
            </div>
        </div>
        """.format(map=gamemap,
            recentgames=recentgames, toprace=toprace)
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["map"] = map


def mode(sel):
    ret = ""
    gs = dbselectors.ModeSelector()
    gs.copyfrom(sel)
    mode = gs.single(sel.pathid)
    if mode is None:
        ret = "<div class='center'><h2>No such Mode.</h2></div>"
    else:
        recentgames = ""
        for gid, game in sorted(list(mode["recentgames"].items()),
            key=lambda x: -x[0])[:10]:
                recentgames += '<tr>'
                recentgames += tdlink("game", gid, "Game #%d" % gid)
                recentgames += tdlink("map", game["map"], game["map"])
                recentgames += '<td>%s</td>' % timeutils.durstr(round(
                    game["timeplayed"]))
                recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
                recentgames += '</tr>'
        ret += """
        <div class="center">
            <h2>{mode[name]}</h2>
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Map</th>
                        <th>Duration</th>
                        <th>Played</th>
                    </tr>
                    {recentgames}
                </table>
            </div>
        </div>
        """.format(mode=mode,
            recentgames=recentgames)
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["mode"] = mode
