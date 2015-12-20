# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
onpagecount = 20


def single(request, db, specific):
    ret = ""
    modeselector = dbselectors.get('mode', db)
    modeselector.flags_none()
    mode = modeselector.single(specific)
    if utils.sok(mode):
        # Game List
        pager = web.Pager(request, onpagecount, reversed(mode["games"]))
        recentgames = web.Table(
            ["ID", "Mutators", "Map", "Duration", "Played"])
        gs = dbselectors.get('game', db)
        gs.flags_none()
        for gid in pager.list():
            game = gs.single(gid)
            with recentgames.tr as tr:
                tr(web.link("/game/", gid, "Game #%d" % gid))
                tr(redeclipse(game).mutslist(game, True) or '-')
                tr(web.link("/map/", game["map"], game["map"], True))
                tr(timeutils.durstr(round(game["timeplayed"])))
                tr(timeutils.agohtml(game["time"]))

        ret += """
        <div class="center">
            <h2>{modeimg} {mode[name]}</h2>
            <div class='display-table'>
                <h3>Recent Games</h3>
                {recentgames}
                {pages}
            </div>
        </div>
        """.format(mode=mode,
            modeimg=redeclipse().modeimg(mode["id"], 32),
            recentgames=recentgames.html(),
            pages=pager.html())
    else:
        ret = "<div class='center'><h2>No such mode.</h2></div>"
    return web.page(ret, title="Mode %s" % specific)
