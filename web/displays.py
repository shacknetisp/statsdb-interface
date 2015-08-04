# -*- coding: utf-8 -*-
from . import base
from .base import tdlink, alink
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
    game["map"] = cgi.escape(game["map"])
    if game is None:
        ret = "<div class='center'><h2>No such game.</h2></div>"
    else:
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
            playersstr += tdlink("player", player["handle"], player["name"])
            playersstr += "<td>%s</td>" % (dbselectors.scorestr(game,
                player["score"]))
            playersstr += tdlink("player", player["handle"], player["handle"])
            playersstr += "<td>%d%%</td>" % (
                player["timealive"] / game["timeplayed"] * 100)
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