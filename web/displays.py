# -*- coding: utf-8 -*-
from . import base
from .base import tdlink, alink, tdlinkp, alinkp
from . import page
import dbselectors
from redeclipse import redeclipse
import cgi
import timeutils
import caches
displays = {}


def tableweapon(weapon, totalwielded):
    weap = cgi.escape(weapon["name"])
    weapons = ""
    weapons += "<tr>"
    weapons += "%s" % tdlink("weapon", weap,
        '%s %s' % (redeclipse().weaponimg(weap), cgi.escape(weap)),
        e=False)
    weapons += "<td>%d%%</td>" % (
        weapon["timeloadout"] / max(1, totalwielded) * 100)
    weapons += "<td>%d%%</td>" % (
        weapon["timewielded"] / max(1, totalwielded) * 100)
    weapons += "<td><span class='explain' title='%d %d'>%d</span></td>" % (
        weapon["damage1"] / (max(weapon["timewielded"], 1) / 60),
        weapon["damage2"] / (max(weapon["timewielded"], 1) / 60),
        (weapon["damage1"] + weapon["damage2"]) / (
            max(weapon["timewielded"], 1) / 60))
    weapons += "<td><span class='explain' title='%d %d'>%d</span></td>" % (
        weapon["frags1"] / (max(weapon["timewielded"], 1) / 60),
        weapon["frags2"] / (max(weapon["timewielded"], 1) / 60),
        (weapon["frags1"] + weapon["frags2"]) / (
            max(weapon["timewielded"], 1) / 60),)
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
        listcount = 20
        gs = dbselectors.GameSelector(sel)
        gs.minimal = "basic"
        firstgame = gs.single(server["games"][0])
        recentgames = ""
        currentpage = page.calc(sel, len(server["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = server["games"][-(gid + 1)]
            except IndexError:
                break
            game = gs.single(gid)
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                redeclipse().modeimg(game["mode"]), e=False)
            recentgames += "<td>%s</td>" % (
                redeclipse().mutslist(game, True) or '-')
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
            <a href="/game/{fgid}">Game #{fgid}</a>.<br>
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Mode</th>
                        <th>Mutators</th>
                        <th>Map</th>
                        <th>Duration</th>
                        <th>Played</th>
                    </tr>
                    {recentgames}
                </table>
                {pages}
            </div>
        </div>
        """.format(server=server, recentgames=recentgames,
            servergames=len(server["games"]),
            fgtime=timeutils.agohtml(firstgame["time"]), fgid=firstgame["id"],
            pages=page.make(
            sel.webpath, currentpage, len(server["games"]), listcount
            ))
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
                    game["mode"] == redeclipse(game).modes["race"]
                    and (game["mutators"] & redeclipse(game).mutators["timed"])
                    else -1
                    )), key=lambda x: game["teams"][x]["score"] == 0):
                team = game["teams"][team]
                teamlist[team["team"]] = team
                teamsstr += "<tr>"
                teamsstr += "<td>%s %s</td>" % (
                    redeclipse(game).teamimg(team["team"]),
                    cgi.escape(team["name"]))
                teamsstr += "<td>%s</td>" % (redeclipse(game).scorestr(game,
                    team["score"]))
                teamsstr += "</tr>"
        playersstr = ""
        for player in game["players"]:
            playersstr += "<tr>"
            playersstr += tdlinkp("player", player["handle"], player["name"])
            playersstr += "<td>%s</td>" % (redeclipse(game).scorestr(game,
                player["score"]))
            playersstr += tdlinkp("player", player["handle"], player["handle"])
            playersstr += "<td>%s</td>" % (
                timeutils.durstr(player["timealive"]))
            playersstr += "<td>%d</td>" % player["frags"]
            playersstr += "<td>%d</td>" % player["deaths"]
            if game["mode"] != redeclipse(game).modes["race"]:
                playersstr += "<td>%d</td>" % (player["score"] /
                    (player["timealive"] / 60))
                playersstr += "<td>%d</td>" % (player["damage"] /
                    (player["timealive"] / 60))
                playersstr += "<td>%d</td>" % (player["frags"] /
                    (player["timealive"] / 60))
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
        weapontext = ""
        totalwielded = sum([w['timewielded']
            for w in list(game['weapons'].values())
            if w['timewielded'] is not None])
        for weap in redeclipse().weaponlist:
            weapon = game['weapons'][weap]
            if weapon['timeloadout']:
                weapontext += tableweapon(weapon, totalwielded)
        ret += """
        <div class="center">
            <h2>Game #{game[id]}: {modestr} on {mapstr}</h2>
            {mutsstr}
            Duration: {duration}<br>
            Played: {agohtml}<br>
            Server: <a
            href="/server/{server[handle]}">{server[desc]}</a><br>
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
                        {pms}
                    </tr>
                    {players}
                </table>
            </div>
            {captures}
            {bombings}
            {ffarounds}
            <div class='display-table small-table'>
                <h3>Weapon Statistics</h3>
                <table>
                    <tr>
                        {tableweaponlabels}
                    </tr>
                    {weapons}
                </table>
            </div>
        </div>
        """.format(
            modestr="%s" % (alink("mode", game["mode"],
                redeclipse(game).modeimg(game["mode"], 32), e=False)),
            mutsstr=("Mutators: %s<br>" % redeclipse(game).mutslist(
                game, True, True))
            if game['mutators'] else '',
            mapstr=alink("map", game["map"], game["map"]),
            agohtml=timeutils.agohtml(game["time"]),
            duration=timeutils.durstr(game["timeplayed"]),
            game=game, server=server, players=playersstr,
            captures=captures, bombings=bombings, ffarounds=ffarounds,
            weapons=weapontext, tableweaponlabels=tableweaponlabels(),
            pms="""
            <th>SPM</th>
            <th>DPM</th>
            <th>FPM</th>
            """ if game["mode"] != redeclipse(game).modes["race"] else "",
            teamtable=("""
            <div class='display-table small-table'>
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
        gs.minimal = "basicserver"
        game = gs.single(gid)
        gamestext += '<tr>'
        gamestext += tdlink("game", gid, "Game #%d" % gid)
        gamestext += tdlink("mode",
            game["mode"],
            redeclipse(game).modeimg(game["mode"]), e=False)
        gamestext += "<td>%s</td>" % (redeclipse(game).mutslist(
            game, True
            ) or '-')
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
        <h3>{gamenum} Recorded</h3>
        <table>
            <tr>
                <th>ID</th>
                <th>Mode</th>
                <th>Mutators</th>
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
        ), gamenum=gs.numgames())
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
                    redeclipse(game).modeimg(game["mode"]), e=False)
                recentgames += "<td>%s</td>" % (
                    redeclipse(game).mutslist(
                    game, True
                    ) or '-')
                recentgames += tdlink("map", game["map"], game["map"])
                recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
                recentgames += '<td>%s</td>' % cgi.escape(entry["name"])
                recentgames += '<td>%s</td>' % redeclipse(game).scorestr(game,
                    entry["score"])
                recentgames += '<td>%d</td>' % entry["frags"]
                recentgames += '<td>%d</td>' % entry["deaths"]
                recentgames += '</tr>'
        recentweapons = ""
        try:
            fratio = "%.2f [%d / %d]" % ((player["recent"]["frags"] /
                max(1, player["recent"]["deaths"])),
                    player["recent"]["frags"],
                    player["recent"]["deaths"])
        except TypeError:
            fratio = "-"
        totalwielded = sum([w['timewielded']
            for w in list(player['recent']['weapons'].values())
            if w['timewielded'] is not None])
        for weap in redeclipse().weaponlist:
            weapon = player['recent']['weapons'][weap]
            if weapon['timeloadout'] is not None:
                recentweapons += tableweapon(weapon, totalwielded)
        gs = dbselectors.GameSelector(sel)
        gs.minimal = "basic"
        firstago = '<a href="/game/%d">%s</a>' % (min(player["games"]),
            timeutils.agohtml(gs.single(min(player["games"]))["time"]))
        lastago = '<a href="/game/%d">%s</a>' % (max(player["games"]),
            timeutils.agohtml(gs.single(max(player["games"]))["time"]))
        try:
            dpm = "%d [Recent: %d]" % (round(player["alltime"]["damage"]
            / (player["alltime"]["timealive"] / 60)),
                round(player["recent"]["damage"]
            / (player["recent"]["timealive"] / 60)))
        except:
            dpm = "-"
        topmap = "-"
        maps = {}
        for row in sel.db.con.execute('''SELECT map FROM games
            WHERE id IN (SELECT game
            FROM game_players WHERE handle = ?)''', (player["handle"],)):
                if row[0] not in maps:
                    maps[row[0]] = 0
                maps[row[0]] += 1
        if maps:
            t = sorted(maps, key=lambda x: -maps[x])[0]
            topmap = alink("map", t, t)
        ret += """
        <div class="center">
            <h2>{player[name]}</h2>
            <h3>{player[handle]}</h3>
            <div class="colcontainer">
            <div class="leftcol">
            First appeared: {firstago}<br>
            Last appeared: {lastago}<br>
            </div>
            <div class="rightcol">
            Most played map: {topmap}<br>
            Playing time: {timeplayed}<br>
            </div>
            </div>
            <div style="clear: both;"></div>
            <h3>Recent Games</h3>
            Frag Ratio: {fratio}<br>
            DPM: {dpm}<br>
            <div class='display-table'>
                <table>
                    <tr>
                        <th>Game</th>
                        <th>Mode</th>
                        <th>Mutators</th>
                        <th>Map</th>
                        <th>Time</th>
                        <th>Played As</th>
                        <th>Score</th>
                        <th>Frags</th>
                        <th>Deaths</th>
                    </tr>
                    {recentgames}
                </table>
                <h5 style="text-align: left;">
                <a href="/display/playergames/{player[handle]}">
                All Games...</a></h5>
            </div>
            <div class='display-table small-table'>
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
            dpm=dpm, topmap=topmap, timeplayed=timeutils.durstr(
                player["alltime"]["timeactive"],
                skip="s", skiplow=False,
                full=True,
                ))
    return base.page(sel, ret, title="%s" % sel.pathid)
displays["player"] = player


def playergames(sel):
    listcount = 20
    ret = ""
    gs = dbselectors.PlayerSelector(sel)
    gamesel = dbselectors.GameSelector(sel)
    player = gs.single(sel.pathid)
    if player is None:
        ret = "<div class='center'><h2>No such player.</h2></div>"
    else:
        player["name"] = cgi.escape(player["name"])
        recentgames = ""
        currentpage = page.calc(sel, len(player["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = player["games"][-(gid + 1)]
            except IndexError:
                break
            gamesel.minimal = "basicplayer"
            game = gamesel.single(gid)
            entry = [p for p in game["players"]
            if p["handle"] == player["handle"]][0]
            recentgames += '<tr>'
            recentgames += tdlink("game", gid,
                "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                redeclipse.modeimg(game["mode"]), e=False)
            recentgames += "<td>%s</td>" % (redeclipse.mutslist(
                game, True
                ) or '-')
            recentgames += tdlink("map", game["map"], game["map"])
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '<td>%s</td>' % cgi.escape(entry["name"])
            recentgames += '<td>%s</td>' % redeclipse.scorestr(game,
                entry["score"])
            recentgames += '<td>%d</td>' % entry["frags"]
            recentgames += '<td>%d</td>' % entry["deaths"]
            recentgames += '</tr>'
        ret += """
        <div class="center">
            <h2><a href="/player/{player[handle]}">
            {player[handle]}</a>: Games</h2>
            <div class='display-table'>
                <table>
                    <tr>
                        <th>Game</th>
                        <th>Mode</th>
                        <th>Mutators</th>
                        <th>Map</th>
                        <th>Time</th>
                        <th>Played As</th>
                        <th>Score</th>
                        <th>Frags</th>
                        <th>Deaths</th>
                    </tr>
                    {recentgames}
                </table>
                {pages}
            </div>
        </div>
        """.format(recentgames=recentgames, player=player, pages=page.make(
        sel.webpath, currentpage, len(player["games"]), listcount
        ))
    return base.page(sel, ret, title="%s: Games" % sel.pathid)
displays["playergames"] = playergames


def weapon_disp(sel):
    ret = ""
    gs = dbselectors.WeaponSelector(sel)
    totalwielded = sum([w['alltime']['timewielded']
        for w in list(gs.getdict().values())])
    weapon = gs.single(sel.pathid)["alltime"]
    if weapon is None or sel.pathid not in redeclipse().weaponlist:
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
    for name in redeclipse().weaponlist:
        weapon = gs.single(name)["alltime"]
        try:
            weapons += tableweapon(weapon, totalwielded)
        except TypeError:
            pass
    ret += """
    <div class="center">
        <h2>Weapons</h2>
        <div class='display-table small-table'>
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
        gs.minimal = "basic"
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
    s.minimal = "basic"
    players = s.getdict()
    playertable = ""
    currentpage = page.calc(sel, s.numplayers(), listcount)
    for player in sorted(players, key=lambda x: -players[x]["games"][-1])[
        currentpage:currentpage + listcount]:
        player = players[player]
        gs.minimal = "basic"
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
        sel.webpath, currentpage, s.numplayers(), listcount
        ))
    return base.page(sel, ret, title="Players")
displays["players"] = players


def gmap(sel):
    listcount = 20
    ret = ""
    gs = dbselectors.MapSelector(sel)
    gamesel = dbselectors.GameSelector(sel)
    gamesel.minimal = "basic"
    gamemap = gs.single(sel.pathid)
    if gamemap is None:
        ret = "<div class='center'><h2>No such Map.</h2></div>"
    else:
        recentgames = ""
        currentpage = page.calc(sel, len(gamemap["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = gamemap["games"][-(gid + 1)]
            except IndexError:
                break
            game = gamesel.single(gid)
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += tdlink("mode",
                game["mode"],
                redeclipse(game).modeimg(game["mode"]), e=False)
            recentgames += "<td>%s</td>" % (redeclipse(game).mutslist(
                game, True
                ) or '-')
            recentgames += '<td>%s</td>' % timeutils.durstr(round(
                game["timeplayed"]))
            recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
            recentgames += '</tr>'
        toprace = ""
        for race in gamemap["topraces"][:5]:
            toprace += "<tr>"
            toprace += "<td>%s</td>" % (
                timeutils.durstr(race["time"] / 1000, dec=True,
                    full=True))
            toprace += tdlinkp("player",
                race["gameplayer"]["handle"],
                race["gameplayer"]["name"])
            toprace += tdlinkp("player",
                race["gameplayer"]["handle"],
                race["gameplayer"]["handle"] or "-")
            toprace += tdlink("game", race["game"]["id"],
                    "Game #%d" % race["game"]["id"])
            toprace += "<td>%s</td>" % timeutils.agohtml(race["game"]["time"])
            toprace += "</tr>"
        racetimes = """
            <div class='display-table small-table'>
                <h3>Top Race Times</h3>
                <table>
                    <tr>
                        <th>Time</th>
                        <th>Player</th>
                        <th>Handle</th>
                        <th>Game</th>
                        <th>When</th>
                    </tr>
                    {toprace}
                </table>
            </div>
        """.format(toprace=toprace)
        ret += """
        <div class="center">
            <h2>{map[name]}</h2>
            {racetimes}
            <div class='display-table'>
                <h3>Recent Games</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Mode</th>
                        <th>Mutators</th>
                        <th>Duration</th>
                        <th>Played</th>
                    </tr>
                    {recentgames}
                </table>
                {pages}
            </div>
        </div>
        """.format(map=gamemap,
            recentgames=recentgames,
            racetimes=racetimes if gamemap["toprace"]["time"] else '',
            pages=page.make(
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
        gs.minimal = "basic"
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
            maptable += "<td>%s by %s</td>" % (timeutils.durstr(
                gamemap["toprace"]["time"] / 1000, dec=True, full=True),
                    alinkp("player", gamemap["toprace"]["gameplayer"]["handle"],
                        gamemap["toprace"]["gameplayer"]["handle"]
                        or gamemap["toprace"]["gameplayer"]["name"]))
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
    gamesel.minimal = "basic"
    mode = gs.single(sel.pathid)
    if mode is None:
        ret = "<div class='center'><h2>No such Mode.</h2></div>"
    else:
        recentgames = ""
        currentpage = page.calc(sel, len(mode["games"]), listcount)
        for gid in page.getlist(currentpage, listcount):
            try:
                gid = mode["games"][-(gid + 1)]
            except IndexError:
                break
            game = gamesel.single(gid)
            recentgames += '<tr>'
            recentgames += tdlink("game", gid, "Game #%d" % gid)
            recentgames += "<td>%s</td>" % (redeclipse(game).mutslist(
                game, True
                ) or '-')
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
                        <th>Mutators</th>
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
            modeimg=redeclipse().modeimg(mode["id"], 32),
            mode=mode,
            recentgames=recentgames, pages=page.make(
            sel.webpath, currentpage, len(mode['games']), listcount
            ))
    return base.page(sel, ret, title="Mode %s" % sel.pathid)
displays["mode"] = mode


def ranks(sel):
    listcount = 20
    ret = ""
    ranktext = ""
    if sel.pathid in ["spm", "dpm", "fpm"]:
        ranks = caches.caches["spm"].get(sel.pathid, 180)
    elif sel.pathid in ["games"]:
        ranks = caches.caches["plsingle"].get(sel.pathid)
    elif sel.pathid in ["ffa", "ffasurv", "mvp"]:
        ranks = caches.caches["plwinner"].get(sel.pathid, 180)
    else:
        ret = "<div class='center'><h2>No such Ranking</h2></div>"
        return base.page(sel, ret, title="Ranks")
    currentpage = page.calc(sel, len(ranks), listcount)
    for i, e in enumerate(ranks[currentpage:currentpage + listcount]):
        ranktext += "<tr>"
        ranktext += "<td>%d</td>" % (1 + i + (currentpage * listcount))
        ranktext += tdlink("player", e[0], e[0])
        if type(e[1]) is list:
            ranktext += "<td>%d [%d/%d]</td>" % (
                (e[1][0] / max(1, e[1][1])), e[1][0], e[1][1])
        else:
            ranktext += "<td>%d</td>" % e[1]
        ranktext += "</tr>"
    ret += """
    <div class="center">
        <h2>{rank}</h2>
        <div class='display-table'>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Handle</th>
                    <th>{number}</th>
                </tr>
                {ranktext}
            </table>
            {pages}
        </div>
    </div>
    """.format(
        rank={'spm': 'Score per Minute [Last 180 Days]',
            'dpm': 'Damage per Minute [Last 180 Days]',
            'fpm': 'Frags per Minute [Last 180 Days]',
            'games': 'Games [All Time]',
            'ffa': 'FFA Win Ratio [Last 180 Days]',
            'ffasurv': 'FFA Survivor Win Ratio [Last 180 Days]'}[sel.pathid],
        number={'spm': 'SPM',
            'dpm': 'DPM',
            'fpm': 'FPM',
            'games': 'Games',
            'ffa': 'Wins/Losses',
            'ffasurv': 'Wins/Losses',
            }[sel.pathid],
        ranktext=ranktext, pages=page.make(
        sel.webpath, currentpage, len(ranks), listcount
        ))
    return base.page(sel, ret, title="Ranks")
displays["ranks"] = ranks
