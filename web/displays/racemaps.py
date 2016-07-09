# -*- coding: utf-8 -*-
import dbselectors
import web
import timeutils
onpagecount = 15


def multi(request, db):
    mapselector = dbselectors.get('map', db)
    mapselector.flags_none()
    mapselector.weakflags(["race"], True)

    gameselector = dbselectors.get('game', db)
    gameselector.flags_none()

    maps = mapselector.multi()
    mapkeys = [x for x in maps if maps[x]["toprace"]["time"]]
    pager = web.Pager(request, onpagecount,
        sorted(mapkeys, key=lambda x: -maps[x]["games"][-1]))
    maptable = web.Table(["Name", "Games",
        "First Game", "Latest Game", "Best Race Time",
            "Best Endurance Race Time"])
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
            if gmap["toperace"]["time"]:
                tr("%s by %s" % (timeutils.durstr(
                    gmap["toperace"]["time"] / 1000, dec=True, full=True),
                    web.linkif("/player/",
                        gmap["toperace"]["gameplayer"]["handle"],
                        gmap["toperace"]["gameplayer"]["handle"]
                        or gmap["toperace"]["gameplayer"]["name"])
                        )
                    )
            else:
                tr()
    ret = """
    <div class="center">
        <h2>Race Maps</h2>
        <div class='display-table'>
            {maptable}
            {pages}
        </div>
    </div>
    """.format(maptable=maptable.html(), pages=pager.html())
    return web.page(ret, title="Maps")