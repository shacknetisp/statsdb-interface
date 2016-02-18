# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
import cgi
onpagecount = 15


def single(request, db, specific):
    gs = dbselectors.get('game', db)
    gs.flags_none()
    gs.weakflags(["server", "teams",
        "affinities", "rounds", "players", "playerdamage", "weapons"], True)
    ss = dbselectors.get('server', db)
    ss.flags_none()

    game = gs.single(specific)
    ret = ""
    if utils.sok(game):
        server = ss.single(game["server"])
        # Display the server's desc & version from this game.
        serverrow = db.execute(
            """SELECT version,desc,host,port
            FROM game_servers WHERE game = %d""" % game["id"]
            ).fetchone()
        server["version"] = serverrow[0]
        server["desc"] = cgi.escape(serverrow[1]) or cgi.escape(
            "%s:%d" % (serverrow[2], serverrow[3]))

        playerstable = web.Table(
            ["Name", "Score", "Handle", "Alive", "Frags", "Deaths"],
            "Players", "display-table")
        for player in sorted(
            list(game["players"].values()), key=lambda x: (
                redeclipse(game).scorenum(game, x["score"]))):
                with playerstable.tr as tr:
                    tr(web.linkif('/player/', player["handle"], player["name"]))
                    tr(redeclipse(game).scorestr(game, player["score"]))
                    tr(web.linkif('/player/',
                        player["handle"], player["handle"]))
                    tr(timeutils.durstr(player["timealive"]))
                    tr(player["frags"])
                    tr(player["deaths"])

        teamstable = None
        teamlist = {}
        if len(game["teams"]) > 1:
            teamstable = web.Table(
                ["Name", "Score"],
                "Teams", "display-table small-table")
            # Sort depending on score, counting race times
            for team in sorted(sorted(game["teams"],
                key=lambda x: game["teams"][x]["score"] * (
                    1 if
                    game["mode"] == redeclipse(game).modes["race"]
                    and (game["mutators"] & redeclipse(game).mutators["timed"])
                    else -1
                    )), key=lambda x: game["teams"][x]["score"] == 0):
                        team = game["teams"][team]
                        teamlist[team["team"]] = team
                        with teamstable.tr as tr:
                            tr("%s %s" % (
                                redeclipse(game).teamimg(team["team"]),
                                cgi.escape(team["name"])
                                ))
                            tr(redeclipse(game).scorestr(game, team["score"]))

        ffarounds = web.Table(["Round", "Winner", "Versus"],
            "Teams", "display-table small-table")
        if "ffarounds" in game:
            donerounds = []
            for ffaround in sorted(game["ffarounds"], key=lambda x: x["round"]):
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
                        versuslist.append(web.linkif(
                            "/player/", ffaround_s["playerhandle"],
                            game["players"][ffaround_s["player"]]["name"]))
                with ffarounds.tr as tr:
                    if haswinner and ffaround["winner"]:
                            tr(ffaround["round"])
                            tr(web.linkif(
                                "/player/", ffaround["playerhandle"],
                                game["players"][ffaround["player"]]["name"]))
                            if versuslist:
                                tr(", ".join(versuslist))
                            else:
                                tr("<i>AI</i>")
                    elif not haswinner:
                        donerounds.append(ffaround["round"])
                        if len(versuslist) == 1:
                            tr(ffaround["round"])
                            tr('<i>AI</i>')
                            tr(", ".join(versuslist))
                        else:
                            tr(ffaround["round"])
                            tr('<i>Epic fail!</i>')
                            tr(", ".join(versuslist))

        affinitiestable = None
        if "captures" in game:
            affinitiestable = web.Table(
                ["Player", "Capturing Team", "Captured Flag"],
                "Flag Captures", "display-table"
                )
            for capture in game["captures"]:
                with affinitiestable.tr as tr:
                    tr(web.linkif('/player/', capture["playerhandle"],
                        game["players"][capture["player"]]["name"]))
                    tr(cgi.escape(teamlist[capture["capturing"]]["name"]))
                    tr(cgi.escape(teamlist[capture["captured"]]["name"]))
        elif "bombings" in game:
            affinitiestable = web.Table(
                ["Player", "Bombing Team", "Bombed Base"],
                "Base Bombings", "display-table"
                )
            for bombing in game["bombings"]:
                with affinitiestable.tr as tr:
                    tr(web.linkif('/player/', bombing["playerhandle"],
                        game["players"][bombing["player"]]["name"]))
                    tr(cgi.escape(teamlist[bombing["bombing"]]["name"]))
                    tr(cgi.escape(teamlist[bombing["bombed"]]["name"]))

        totalwielded = sum([w['timewielded']
            for w in list(game['weapons'].values())
            if w['timewielded'] is not None])
        weaponstable = web.displays.weaponstable(game['weapons'],
            totalwielded, redeclipse(game).weaponlist, version=game)
        if game["mode"] == redeclipse(game).modes['race']:
            weaponstable = None

        ret = """
        <div class="center">
            <h2>Game #{game[id]}: {modestr} on {mapstr}</h2>
            {mutsstr}
            Duration: {duration}<br>
            Played: {agohtml}<br>
            Server: <a
                href="/server/{server[handle]}">{server[desc]}
                [{server[version]}] [{server[handle]}]</a>
            {teams}
            {players}
            {affinities}
            {ffarounds}
            {weapons}
        </div>
        """.format(
            game=game,
            modestr=web.link('/mode/', game["mode"],
                redeclipse(game).modeimg(game["mode"], 32)),
            mutsstr=("Mutators: %s<br>" % redeclipse(game).mutslist(
                game, True, True)) if game['mutators'] else '',
            mapstr=web.link('/map/', game["map"], game["map"]),
            server=server,
            agohtml=timeutils.agohtml(game["time"]),
            duration=timeutils.durstr(game["timeplayed"]),
            players=playerstable.html(True),
            teams=teamstable.html(True) if teamstable is not None else "",
            affinities=affinitiestable.html(True)
                if affinitiestable is not None else "",
            ffarounds=ffarounds.html(True) if "ffarounds" in game else "",
            weapons=weaponstable.html(True)
                if weaponstable is not None else "",
            )
    else:
        ret = "<div class='center'><h2>No such game.</h2></div>"
    return web.page(ret, title="Game %s" % specific)


def multi(request, db):
    gs = dbselectors.get('game', db)
    gs.flags_none()
    gs.weakflags(["server"], True)
    games = gs.multi()
    pager = web.Pager(request, onpagecount, reversed(list(games.keys())))
    table = web.Table(
        ["ID", "Mode", "Mutators", "Server",
            "Map", "Duration", "Played"])
    for gid in pager.list():
        game = games[gid]
        with table.tr as tr:
            tr(web.link('/game/', gid, "Game #%d" % gid))
            tr(web.link('/mode/', game["mode"],
                redeclipse(game).modeimg(game["mode"])))
            tr(redeclipse(game).mutslist(game, True) or '-')
            row = db.execute(
                "SELECT version FROM game_servers WHERE game = %d" % gid
                ).fetchone()
            version = row[0]
            tr("%s [%s]" % (
                web.link('/server/', game["server"], game["server"]),
                version))
            tr(web.link('/map/', game["map"], game["map"], True))
            tr(timeutils.durstr(round(game["timeplayed"])))
            tr(timeutils.agohtml(game["time"]))
    ret = """
    <div class="center display-table">
        <h2>Games</h2>
        <h3>{gamenum} Recorded</h3>
        {table}
        {pages}
    </div>
    """.format(table=table.html(), pages=pager.html(), gamenum=len(games))
    return web.page(ret, title="Games")
