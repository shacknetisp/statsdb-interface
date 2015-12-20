# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
onpagecount = 20


def single(request, db, specific):
    ret = ""
    serverselector = dbselectors.get('server', db)
    serverselector.flags_none()
    serverselector.weakflags(["games"], True)
    server = serverselector.single(specific)
    if utils.sok(server):
        # Game List
        pager = web.Pager(request, onpagecount, reversed(server["games"]))
        recentgames = web.Table(
            ["ID", "Mode", "Mutators", "Duration", "Played"])
        gs = dbselectors.get('game', db)
        gs.flags_none()
        firstgame = gs.single(server["games"][0])
        for gid in pager.list():
            game = gs.single(gid)
            with recentgames.tr as tr:
                tr(web.link("/game/", gid, "Game #%d" % gid))
                tr(web.link("/mode/", game["mode"],
                    redeclipse(game).modeimg(game["mode"])))
                tr(redeclipse(game).mutslist(game, True) or '-')
                tr(timeutils.durstr(round(game["timeplayed"])))
                tr(timeutils.agohtml(game["time"]))

        ret += """
        <div class="center">
            <h2>{server[desc]}</h2>
            <h3>{server[handle]} <i>[{server[authflags]}]</i>:
                Version {server[version]}</h3>
            <a href="redeclipse://{server[host]}:{server[port]}">
            {server[host]}:{server[port]}</a><br>
            {servergames} games recorded.<br>
            First Recorded: {fgtime} with
            <a href="/game/{fgid}">Game #{fgid}</a>.<br>
            <div class='display-table'>
                <h3>Recent Games</h3>
                {recentgames}
                {pages}
            </div>
        </div>
        """.format(server=server, recentgames=recentgames.html(),
            servergames=len(server["games"]),
            fgtime=timeutils.agohtml(firstgame["time"]), fgid=firstgame["id"],
            pages=pager.html())
    else:
        ret = "<div class='center'><h2>No such map.</h2></div>"
    return web.page(ret, title="Map %s" % specific)


def multi(request, db):
    serverselector = dbselectors.get('server', db)
    serverselector.flags_none()
    serverselector.weakflags(['games'], True)

    gameselector = dbselectors.get('game', db)
    gameselector.flags_none()

    servers = serverselector.multi()
    pager = web.Pager(request, onpagecount,
        sorted(servers, key=lambda x: -servers[x]["games"][-1]))
    servertable = web.Table(
        ["Handle", "Description", "Games", "First Game", "Latest Game"])
    for handle in pager.list():
        server = servers[handle]
        firstgame = gameselector.single(server["games"][0])
        latestgame = gameselector.single(server["games"][-1])
        with servertable.tr as tr:
            tr(web.link('/server/', server["handle"], server["handle"], True))
            tr(web.link('/server/', server["handle"], server["desc"], True))
            tr(len(server["games"]))
            tr("%s: %s" % (
                web.link('/game/', firstgame['id'], "#%d" % firstgame["id"]),
                timeutils.agohtml(firstgame["time"])
                ))
            tr("%s: %s" % (
                web.link('/game/', latestgame['id'], "#%d" % latestgame["id"]),
                timeutils.agohtml(latestgame["time"])
                ))
    ret = """
    <div class="center">
        <h2>Servers</h2>
        <div class='display-table'>
            {servertable}
            {pages}
        </div>
    </div>
    """.format(servertable=servertable.html(), pages=pager.html())
    return web.page(ret, title="Maps")