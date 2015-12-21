# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
onpagecount = 20


def single(request, db, specific):
    ret = ""
    mutselector = dbselectors.get('mut', db)
    mutselector.flags_none()
    mut = mutselector.single(specific)
    if utils.sok(mut):
        # Game List
        pager = web.Pager(request, onpagecount, reversed(mut["games"]))
        recentgames = web.Table(
            ["ID", "Mode", "Mutators", "Map", "Duration", "Played"])
        gs = dbselectors.get('game', db)
        gs.flags_none()
        for gid in pager.list():
            game = gs.single(gid)
            with recentgames.tr as tr:
                tr(web.link("/game/", gid, "Game #%d" % gid))
                tr(redeclipse(game).modeimg(game["mode"]))
                tr(redeclipse(game).mutslist(game, True) or '-')
                tr(web.link("/map/", game["map"], game["map"], True))
                tr(timeutils.durstr(round(game["timeplayed"])))
                tr(timeutils.agohtml(game["time"]))

        ret += """
        <div class="center">
            <h2>{mut[id]}</h2>
            <div class='display-table'>
                <h3>Recent Games</h3>
                {recentgames}
                {pages}
            </div>
        </div>
        """.format(mut=mut,
            recentgames=recentgames.html(),
            pages=pager.html())
    else:
        ret = "<div class='center'><h2>No such mutator.</h2></div>"
    return web.page(ret, title="Mutator %s" % specific)
