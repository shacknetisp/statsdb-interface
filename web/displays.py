# -*- coding: utf-8 -*-
from . import base
from .base import tdlink, alink, tdlinkp, alinkp
from . import page
import dbselectors
import redeclipse
import cgi
import timeutils
displays = {}


def tableweapon(weapon, totalwielded):
    weap = cgi.escape(weapon["name"])
    weapons = ""
    weapons += "<tr>"
    weapons += "%s" % tdlink("weapon", weap,
        '%s %s' % (redeclipse.weaponimg(weap), cgi.escape(weap)),
        e=False)
    weapons += "<td>%d%%</td>" % (
        weapon["timeloadout"] / max(1, totalwielded) * 100)
    weapons += "<td>%d%%</td>" % (
        weapon["timewielded"] / max(1, totalwielded) * 100)
    weapons += "<td>%d - %d</td>" % (
        weapon["damage1"] / (max(weapon["timewielded"], 1) / 60),
        weapon["damage2"] / (max(weapon["timewielded"], 1) / 60))
    weapons += "<td>%d - %d</td>" % (
        weapon["frags1"] / (max(weapon["timewielded"], 1) / 60),
        weapon["frags2"] / (max(weapon["timewielded"], 1) / 60))
    weapons += "</tr>"
    return weapons


def tableweaponlabels():
    return """
        <th>Weapon</th>
        <th>Loadout</th>
        <th>Wielded</th>
        <th><abbr title="Damage Per Minute">DPM </abbr></th>
        <th><abbr title="Frags Per Minute">FPM</abbr></th>
    """


def server(sel):
    ret = ""
    ss = dbselectors.ServerSelector(sel, True)
    server = ss.single(sel.pathid)
    if server is None:
        ret = "<div class='center'><h2>No such server.</h2></div>"
    else:
        gs = dbselectors.GameSelector(sel)
        firstgame = gs.single(server["games"][0])
        recentgames = ""
        for gid, game in sorted(list(server["recentgames"].items()),
            key=lambda x: -x[0])[:10]:
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                redeclipse.modeimg(game["mode"]), e=False)
            recentgames += tdlink('map', game["map"], game["map"])
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"]))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        server["desc"] = cgi.escape(server["desc"])
        ret += """
        <div class="center">
            <h2>{server[desc]}</h2>
            <h3>{server[handle]} <i>[{server[flags]}]</i>:
                Version {server[version]}</h3>
            <a href="redeclipse://{server[host]}:{server[port]}">
            {server[host]}:{server[port]}</a><br>
            {servergames} games recorded.<br>
            First Recorded: {fgtime} with
            <a href="/display/game/{fgid}">Game #{fgid}</a>.<br>
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
        """.format(server=server, recentgames=recentgames,
            servergames=len(server["games"]),
            fgtime=timeutils.agohtml(firstgame["time"]), fgid=firstgame["id"])
    return base.page(sel, ret, title="Server %s" % sel.pathid)
displays["server"] = server


def game(sel):
    ret = ""
    gs = dbselectors.GameSelector(sel, True)
    game = gs.single(sel.pathid)
    if game is None:
        ret = "<div class='center'><h2>No such game.</h2></div>"
    else:
        game["map"] = cgi.escape(game["map"])
        ss = dbselectors.ServerSelector(sel)
        server = ss.single(game["server"])
        server["desc"] = cgi.escape(server["desc"])
        teamlist = {}
        teamsstr = ""
        if len(game["teams"]) > 1:
            for team in sorted(sorted(game["teams"],
                key=lambda x: game["teams"][x]["score"] * (
                    1 if
                    game["mode"] == redeclipse.modes["race"]
                    and (game["mutators"] & redeclipse.mutators["timed"])
                    else -1
                    )), key=lambda x: game["teams"][x]["score"] == 0):
                team = game["teams"][team]
                teamlist[team["team"]] = team
                teamsstr += "<tr>"
                teamsstr += "<td>%s %s</td>" % (
                    redeclipse.teamimg(team["team"]),
                    cgi.escape(team["name"]))
                teamsstr += "<td>%s</td>" % (redeclipse.scorestr(game,
                    team["score"]))
                teamsstr += "</tr>"
        playersstr = ""
        for player in game["players"]:
            playersstr += "<tr>"
            playersstr += tdlinkp("player", player["handle"], player["name"])
            playersstr += "<td>%s</td>" % (redeclipse.scorestr(game,
                player["score"]))
            playersstr += tdlinkp("player", player["handle"], player["handle"])
            playersstr += "<td>%s</td>" % (
                timeutils.durstr(player["timealive"]))
            playersstr += "<td>%d</td>" % player["frags"]
            playersstr += "<td>%d</td>" % player["deaths"]
            playersstr += "</tr>"

        ffarounds = ""
        captures = ""
        bombings = ""

        if "ffarounds" in game:
            ffarounds += """
            <div class='display-table'>
                <h3>Rounds</h3>
                <table>
                    <tr>
                        <th>Round</th>
                        <th>Winner</th>
                        <th>Versus</th>
                    </tr>"""
            donerounds = []
            for ffaround in game["ffarounds"]:
                if ffaround["round"] in donerounds:
                    continue
                haswinner = False
                for ffaround_s in game["ffarounds"]:
                    if (ffaround_s["round"] == ffaround["round"]
                    and ffaround_s["winner"]):
                        haswinner = True
                        break
                versuslist = []
                for ffaround_s in game["ffarounds"]:
                    if (ffaround_s["round"] == ffaround["round"]
                    and not ffaround_s["winner"]):
                        versuslist.append(alinkp(
                            "player", ffaround_s["playerhandle"],
                            game["players"][ffaround_s["player"]]["name"]))
                if haswinner and ffaround["winner"]:
                    ffarounds += "<tr>"
                    ffarounds += "<td>%d</td>" % ffaround["round"]
                    ffarounds += tdlinkp(
                        "player", ffaround["playerhandle"],
                        game["players"][ffaround["player"]]["name"])
                    ffarounds += "<td>"
                    ffarounds += ", ".join(versuslist)
                    ffarounds += "</td>"
                    ffarounds += "</tr>"
                elif not haswinner:
                    donerounds.append(ffaround["round"])
                    if len(versuslist) == 1:
                        ffarounds += """<tr><td>%d</td><td><i>A bot</i>
                        </td><td>%s</td></tr>""" % (ffaround["round"],
                            ", ".join(versuslist))
                    else:
                        ffarounds += """<tr><td>%d</td><td><i>Epic fail!</i>
                        </td><td>%s</td></tr>""" % (ffaround["round"],
                            ", ".join(versuslist))
            ffarounds += "</table></div>"

        if "captures" in game:
            captures += """
            <div class='display-table'>
                <h3>Flag Captures</h3>
                <table>
                    <tr>
                        <th>Player</th>
                        <th>Capturing Team</th>
                        <th>Captured Flag</th>
                    </tr>"""
            for capture in game["captures"]:
                captures += "<tr>"
                captures += tdlinkp(
                        "player", capture["playerhandle"],
                        game["players"][capture["player"]]["name"])
                captures += "<td>%s</td>" % (cgi.escape(
                    teamlist[capture["capturing"]]["name"],
                    ))
                captures += "<td>%s</td>" % (cgi.escape(
                    teamlist[capture["captured"]]["name"],
                    ))
                captures += "</tr>"
            captures += "</table></div>"

        if "bombings" in game:
            bombings += """
            <div class='display-table'>
                <h3>Base Bombings</h3>
                <table>
                    <tr>
                        <th>Player</th>
                        <th>Bombing Team</th>
                        <th>Bombed Base</th>
                    </tr>"""
            for bombing in game["bombings"]:
                bombings += "<tr>"
                bombings += tdlinkp(
                        "player", bombing["playerhandle"],
                        game["players"][bombing["player"]]["name"])
                bombings += "<td>%s</td>" % (cgi.escape(
                    teamlist[bombing["bombing"]]["name"],
                    ))
                bombings += "<td>%s</td>" % (cgi.escape(
                    teamlist[bombing["bombing"]]["name"],
                    ))
                bombings += "</tr>"
            bombings += "</table></div>"

        ret += """
        <div class="center">
            <h2>Game #{game[id]}: {modestr} on {mapstr}</h2>
            Duration: {duration}<br>
            Played: {agohtml}<br>
            Server: <a
            href="/display/server/{server[handle]}">{server[desc]}</a><br>
            {teamtable}
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
            {captures}
            {bombings}
            {ffarounds}
        </div>
        """.format(
            modestr=alink("mode", game["mode"],
                redeclipse.modeimg(game["mode"], 32), e=False),
            mapstr=alink("map", game["map"], game["map"]),
            agohtml=timeutils.agohtml(game["time"]),
            duration=timeutils.durstr(game["timeplayed"]),
            game=game, server=server, players=playersstr,
            captures=captures, bombings=bombings, ffarounds=ffarounds,
            teamtable=("""
            <div class='display-table'>
                <h3>Teams</h3>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Score</th>
                    </tr>
                    %s
                </table>
            </div>
            """ % teamsstr) if teamsstr else "")
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["game"] = game


def games(sel):
    listcount = 20
    if sel.pathid:
        global game
        return game(sel)
    ret = ""
    gs = dbselectors.GameSelector(sel)
    currentpage = page.calc(sel, gs.numgames(), listcount)
    gamestext = ""
    for gid in page.getlist(currentpage, listcount):
        try:
            gid = gs.getrid()[-(gid + 1)]
        except IndexError:
            break
        game = gs.single(gid)
        gamestext += '<tr>'
        gamestext += tdlink("game", gid, "Game #%d" % gid)
        gamestext += tdlink("mode",
            game["mode"],
            redeclipse.modeimg(game["mode"]), e=False)
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        desc = ss.single(game["server"])["desc"]
        gamestext += tdlink('server', game["server"], desc)
        gamestext += tdlink('map', game["map"], game["map"])
        gamestext += '<td>%s</td>' % timeutils.durstr(round(
            game["timeplayed"]))
        gamestext += '<td>%s</td>' % timeutils.agohtml(game["time"])
        gamestext += '</tr>'
    ret += """
    <div class="center display-table">
        <h2>Games</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Mode</th>
                <th>Server</th>
                <th>Map</th>
                <th>Duration</th>
                <th>Played</th>
            </tr>
            {games}
        </table>
        {pages}
    </div>
    """.format(games=gamestext, pages=page.make(
        sel.webpath, currentpage, gs.numgames(), listcount
        ))
    return base.page(sel, ret, title="Games")
displays["games"] = games


def player(sel):
    ret = ""
    gs = dbselectors.PlayerSelector(sel)
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
                    "Game #%d" % gid)
                recentgames += tdlink("mode",
                    game["mode"],
                    redeclipse.modeimg(game["mode"]), e=False)
                recentgames += tdlink("map", game["map"], game["map"])
                recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
                recentgames += '<td>%s</td>' % cgi.escape(entry["name"])
                recentgames += '<td>%s</td>' % redeclipse.scorestr(game,
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
            for weap in redeclipse.weaponlist:
                weapon = player['recent']['weapons'][weap]
                recentweapons += tableweapon(weapon, totalwielded)
        except TypeError:
            pass
        gs = dbselectors.GameSelector(sel)
        firstago = '<a href="/display/game/%d">%s</a>' % (min(player["games"]),
            timeutils.agohtml(gs.single(min(player["games"]))["time"]))
        lastago = '<a href="/display/game/%d">%s</a>' % (max(player["games"]),
            timeutils.agohtml(gs.single(max(player["games"]))["time"]))
        try:
            dpm = round(player["recent"]["damage"]
            / (player["recent"]["timealive"] / 60))
        except:
            dpm = 0
        ret += """
        <div class="center">
            <h2>{player[name]}</h2>
            <h3>{player[handle]}</h3>
            First appeared: {firstago}<br>
            Last appeared: {lastago}<br>
            <h3>Recent Games</h3>
            Frag Ratio: {fratio}<br>
            DPM: {dpm}<br>
            <div class='display-table'>
                <table>
                    <tr>
                        <th>Game</th>
                        <th>Mode</th>
                        <th>Map</th>
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
                        {tableweaponlabels}
                    </tr>
                    {recentweapons}
                </table>
            </div>
        </div>
        """.format(recentgames=recentgames,
            player=player, firstago=firstago, lastago=lastago,
            fratio=fratio,
            recentweapons=recentweapons,
            tableweaponlabels=tableweaponlabels(),
            dpm=dpm)
    return base.page(sel, ret, title="Game %s" % sel.pathid)
displays["player"] = player


def weapon_disp(sel):
    ret = ""
    gs = dbselectors.WeaponSelector(sel)
    totalwielded = sum([w['alltime']['timewielded']
        for w in list(gs.getdict().values())])
    weapon = gs.single(sel.pathid)["alltime"]
    if weapon is None or sel.pathid not in redeclipse.weaponlist:
        ret = "<div class='center'><h2>No such weapon.</h2></div>"
    else:
        weapons = ""
        try:
            weapons += tableweapon(weapon, totalwielded)
        except TypeError:
            pass
        ret += """
        <div class="center">
            <h2>{weapon[name]}</h2>
            <div class='display-table'>
                <table>
                    <tr>
                        {tableweaponlabels}
                    </tr>
                    {weapons}
                </table>
            </div>
        </div>
        """.format(weapon=weapon, weapons=weapons,
            tableweaponlabels=tableweaponlabels())
    try:
        return base.page(sel, ret, title="%s" % sel.pathid.capitalize())
    except AttributeError:
        return base.page(sel, ret)
displays["weapon"] = weapon_disp


def weapons(sel):
    if sel.pathid:
        return weapon_disp(sel)
    ret = ""
    gs = dbselectors.WeaponSelector(sel)
    weapons = ""
    totalwielded = sum([w['alltime']['timewielded']
        for w in list(gs.getdict().values())])
    for name in redeclipse.weaponlist:
        weapon = gs.single(name)["alltime"]
        try:
            weapons += tableweapon(weapon, totalwielded)
        except TypeError:
            pass
    ret += """
    <div class="center">
        <h2>Weapons</h2>
        <div class='display-table'>
            <table>
                <tr>
                    {tableweaponlabels}
                </tr>
                {weapons}
            </table>
        </div>
    </div>
    """.format(weapons=weapons, tableweaponlabels=tableweaponlabels())
    return base.page(sel, ret, title="Weapons")
displays["weapons"] = weapons


def servers(sel):
    listcount = 20
    if sel.pathid:
        global server
        return server(sel)
    ret = ""
    gs = dbselectors.GameSelector(sel)
    s = dbselectors.ServerSelector(sel)
    servers = s.getdict()
    servertable = ""
    currentpage = page.calc(sel, len(servers), listcount)
    for server in sorted(servers, key=lambda x: -servers[x]["games"][-1])[
        currentpage:currentpage + listcount]:
        server = servers[server]
        firstgame = gs.single(server["games"][0])
        latestgame = gs.single(server["games"][-1])
        servertable += "<tr>"
        servertable += tdlink("server", server["handle"],
            "%s" % (cgi.escape(server["handle"])), False)
        servertable += tdlink("server", server["handle"],
            "%s" % (cgi.escape(server["desc"])), False)
        servertable += "<td>%d</td>" % len(server["games"])
        servertable += "<td>%s: %s</td>" % (alink("game", firstgame["id"],
            "#%d" % (firstgame["id"]), False),
                timeutils.agohtml(firstgame["time"]))
        servertable += "<td>%s: %s</td>" % (alink("game", latestgame["id"],
            "#%d" % (latestgame["id"]), False),
                timeutils.agohtml(latestgame["time"]))
        servertable += "</tr>"
    ret += """
    <div class="center">
        <h2>Servers</h2>
        <div class='display-table'>
            <table>
                <tr>
                    <th>Handle</th>
                    <th>Server</th>
                    <th>Games</th>
                    <th>First Game</th>
                    <th>Latest Game</th>
                </tr>
                {servertable}
            </table>
            {pages}
        </div>
    </div>
    """.format(servertable=servertable, pages=page.make(
        sel.webpath, currentpage, len(servers), listcount
        ))
    return base.page(sel, ret, title="Servers")
displays["servers"] = servers


def players(sel):
    listcount = 20
    if sel.pathid:
        global player
        return player(sel)
    ret = ""
    gs = dbselectors.GameSelector(sel)
    s = dbselectors.PlayerSelector(sel)
    players = s.getdict()
    playertable = ""
    currentpage = page.calc(sel, len(players), listcount)
    for player in sorted(players, key=lambda x: -players[x]["games"][-1])[
        currentpage:currentpage + listcount]:
        player = players[player]
        gs.minimal = True
        firstgame = gs.single(player["games"][0])
        latestgame = gs.single(player["games"][-1])
        playertable += "<tr>"
        playertable += tdlink("player", player["handle"],
            "%s" % (cgi.escape(player["name"])), False)
        playertable += tdlink("player", player["handle"],
            "%s" % (cgi.escape(player["handle"])), False)
        playertable += "<td>%d</td>" % len(player["games"])
        playertable += "<td>%s: %s</td>" % (alink("game", firstgame["id"],
            "#%d" % (firstgame["id"]), False),
                timeutils.agohtml(firstgame["time"]))
        playertable += "<td>%s: %s</td>" % (alink("game", latestgame["id"],
            "#%d" % (latestgame["id"]), False),
                timeutils.agohtml(latestgame["time"]))
        playertable += "</tr>"
    ret += """
    <div class="center">
        <h2>Players</h2>
        <div class='display-table'>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Handle</th>
                    <th>Games</th>
                    <th>First Game</th>
                    <th>Latest Game</th>
                </tr>
                {playertable}
            </table>
            {pages}
        </div>
    </div>
    """.format(playertable=playertable, pages=page.make(
        sel.webpath, currentpage, len(players), listcount
        ))
    return base.page(sel, ret, title="Players")
displays["players"] = players


def gmap(sel):
    listcount = 20
    ret = ""
    gs = dbselectors.MapSelector(sel)
    gamesel = dbselectors.GameSelector(sel)
    gamemap = gs.single(sel.pathid)
    if gamemap is None:
        ret = "<div class='center'><h2>No such Map.</h2></div>"
    else:
        recentgames = ""
        currentpage = page.calc(sel, len(gamemap["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = gamemap["games"][gid]
            except IndexError:
                break
            game = gamesel.single(gid)
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                redeclipse.modeimg(game["mode"]), e=False)
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"]))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        toprace = ""
        if gamemap["toprace"]["time"]:
            toprace = """<h3>Best Time: %s by %s (%s)</h3>""" % (
                timeutils.durstr(gamemap["toprace"]["time"] / 1000, dec=True,
                    full=True),
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
                {pages}
            </div>
        </div>
        """.format(map=gamemap,
            recentgames=recentgames, toprace=toprace, pages=page.make(
            sel.webpath, currentpage, len(gamemap['games']), listcount
            ))
    return base.page(sel, ret, title="Map %s" % sel.pathid)
displays["map"] = gmap


def maps(sel):
    listcount = 20
    if sel.pathid:
        global gmap
        return gmap(sel)
    ret = ""
    gs = dbselectors.GameSelector(sel)
    s = dbselectors.MapSelector(sel)
    maps = s.getdict()
    maptable = ""
    currentpage = page.calc(sel, len(maps), listcount)
    for mapname in sorted(maps, key=lambda x: -maps[x]["games"][-1])[
        currentpage:currentpage + listcount]:
        gamemap = maps[mapname]
        gs.minimal = True
        firstgame = gs.single(gamemap["games"][0])
        latestgame = gs.single(gamemap["games"][-1])
        maptable += "<tr>"
        maptable += tdlink("map", gamemap["name"],
            "%s" % (cgi.escape(gamemap["name"])), False)
        maptable += "<td>%d</td>" % len(gamemap["games"])
        maptable += "<td>%s: %s</td>" % (alink("game", firstgame["id"],
            "#%d" % (firstgame["id"]), False),
                timeutils.agohtml(firstgame["time"]))
        maptable += "<td>%s: %s</td>" % (alink("game", latestgame["id"],
            "#%d" % (latestgame["id"]), False),
                timeutils.agohtml(latestgame["time"]))
        if gamemap["toprace"]["time"]:
            maptable += "<td>%s</td>" % timeutils.durstr(
                gamemap["toprace"]["time"] / 1000, dec=True, full=True)
        else:
            maptable += "<td></td>"
        maptable += "</tr>"
    ret += """
    <div class="center">
        <h2>Maps</h2>
        <div class='display-table'>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Games</th>
                    <th>First Game</th>
                    <th>Latest Game</th>
                    <th>Best Time</th>
                </tr>
                {maptable}
            </table>
            {pages}
        </div>
    </div>
    """.format(maptable=maptable, pages=page.make(
        sel.webpath, currentpage, len(maps), listcount
        ))
    return base.page(sel, ret, title="Maps")
displays["maps"] = maps


def mode(sel):
    listcount = 20
    ret = ""
    gs = dbselectors.ModeSelector(sel, True)
    gamesel = dbselectors.GameSelector(sel)
    mode = gs.single(sel.pathid)
    if mode is None:
        ret = "<div class='center'><h2>No such Mode.</h2></div>"
    else:
        recentgames = ""
        currentpage = page.calc(sel, len(mode["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = mode["games"][gid]
            except IndexError:
                break
            game = gamesel.single(gid)
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("map", game["map"], game["map"])
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"]))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        ret += """
        <div class="center">
            <h2>{modeimg} {mode[name]}</h2>
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
                {pages}
            </div>
        </div>
        """.format(
            modeimg=redeclipse.modeimg(mode["id"], 32),
            mode=mode,
            recentgames=recentgames, pages=page.make(
            sel.webpath, currentpage, len(mode['games']), listcount
            ))
    return base.page(sel, ret, title="Mode %s" % sel.pathid)
displays["mode"] = mode
