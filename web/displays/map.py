# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
onpagecount = 15


def single(request, db, specific):
    ret = ""
    mapselector = dbselectors.get('map', db)
    mapselector.flags_none()
    mapselector.weakflags(["race"], True)
    gmap = mapselector.single(specific)
    if utils.sok(gmap):
        # Game List
        pager = web.Pager(request, onpagecount, reversed(gmap["games"]))
        recentgames = web.Table(
            ["ID", "Mode", "Mutators", "Duration", "Played"])
        gs = dbselectors.get('game', db)
        gs.flags_none()
        for gid in pager.list():
            game = gs.single(gid)
            with recentgames.tr as tr:
                tr(web.link("/game/", gid, "Game #%d" % gid))
                tr(web.link("/mode/", game["mode"],
                    redeclipse(game).modeimg(game["mode"])))
                tr(redeclipse(game).mutslist(game, True) or '-')
                tr(timeutils.durstr(round(game["timeplayed"])))
                tr(timeutils.agohtml(game["time"]))

        # Race Times
        racetable = web.Table(["Time", "Player", "Handle", "Game", "When"])
        for race in gmap["topraces"][:3]:
            with racetable.tr as tr:
                tr(timeutils.durstr(race["time"] / 1000, dec=True, full=True))
                tr(web.linkif('/player/',
                    race["gameplayer"]["handle"], race["gameplayer"]["name"]))
                tr(web.linkif('/player/',
                    race["gameplayer"]["handle"],
                    race["gameplayer"]["handle"] or '-'))
                tr(web.link('/game/', race["game"]["id"],
                    "Game #%d" % race["game"]["id"]))
                tr(timeutils.agohtml(race["game"]["time"]))
        racetimes = """
        <div class='display-table small-table'>
            <h3>Top Race Times</h3>
            %s
        </div>
        """ % racetable.html()

        eracetable = web.Table(["Time", "Player", "Handle", "Game", "When"])
        for race in gmap["toperaces"][:3]:
            with eracetable.tr as tr:
                tr(timeutils.durstr(race["time"] / 1000, dec=True, full=True))
                tr(web.linkif('/player/',
                    race["gameplayer"]["handle"], race["gameplayer"]["name"]))
                tr(web.linkif('/player/',
                    race["gameplayer"]["handle"],
                    race["gameplayer"]["handle"] or '-'))
                tr(web.link('/game/', race["game"]["id"],
                    "Game #%d" % race["game"]["id"]))
                tr(timeutils.agohtml(race["game"]["time"]))
        eracetimes = """
        <div class='display-table small-table'>
            <h3>Top Endurance Race Times</h3>
            %s
        </div>
        """ % eracetable.html()

        ret += """
        <div class="center">
            <h2>{map[name]}</h2>
            {racetimes}
            {eracetimes}
            <div class='display-table'>
                <h3>Recent Games</h3>
                {recentgames}
                {pages}
            </div>
        </div>
        """.format(map=gmap,
            recentgames=recentgames.html(),
            racetimes=racetimes if gmap["toprace"]["time"] else '',
            eracetimes=eracetimes if gmap["toperace"]["time"] else '',
            pages=pager.html())
    else:
        ret = "<div class='center'><h2>No such map.</h2></div>"
    return web.page(ret, title="Map %s" % specific)


def multi(request, db):
    mapselector = dbselectors.get('map', db)
    mapselector.flags_none()
    mapselector.weakflags(["race"], True)

    gameselector = dbselectors.get('game', db)
    gameselector.flags_none()

    maps = mapselector.multi()
    pager = web.Pager(request, onpagecount,
        sorted(maps, key=lambda x: -maps[x]["games"][-1]))
    maptable = web.Table(["Name", "Games",
        "First Game", "Latest Game", '<a href="/racemaps">Best Race Time</a>'])
    for mapname in pager.list():
        gmap = maps[mapname]
        firstgame = gameselector.single(gmap["games"][0])
        latestgame = gameselector.single(gmap["games"][-1])
        with maptable.tr as tr:
            tr(web.link('/map/', gmap["name"], gmap["name"], True))
            tr(len(gmap["games"]))
            tr("%s: %s" % (
                web.link('/game/', firstgame['id'], "#%d" % firstgame["id"]),
                timeutils.agohtml(firstgame["time"])
                ))
            tr("%s: %s" % (
                web.link('/game/', latestgame['id'], "#%d" % latestgame["id"]),
                timeutils.agohtml(latestgame["time"])
                ))
            if gmap["toprace"]["time"]:
                tr("%s by %s" % (timeutils.durstr(
                    gmap["toprace"]["time"] / 1000, dec=True, full=True),
                    web.linkif("/player/",
                        gmap["toprace"]["gameplayer"]["handle"],
                        gmap["toprace"]["gameplayer"]["handle"]
                        or gmap["toprace"]["gameplayer"]["name"])
                        )
                    )
            else:
                tr()
    ret = """
    <div class="center">
        <h2>Maps</h2>
        <div class='display-table'>
            {maptable}
            {pages}
        </div>
    </div>
    """.format(maptable=maptable.html(), pages=pager.html())
    return web.page(ret, title="Maps")