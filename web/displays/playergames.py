# -*- coding: utf-8 -*-
import utils
import web
import dbselectors
import cgi
import timeutils
from redeclipse import redeclipse
onpagecount = 15


def single(request, db, specific):
    ps = dbselectors.get('player', db)
    ps.flags_none()
    ps.weakflags(['games'], True)
    gs = dbselectors.get('game', db)
    gs.flags_none()
    gs.weakflags(['players'], True)
    player = ps.single(specific)
    if utils.sok(player):
        table = web.Table(["Game", "Mode", "Mutators",
            "Map", "Time", "Played As", "Score", "Frags", "Deaths"])
        pager = web.Pager(request, onpagecount, reversed(player["games"]))
        for gid in pager.list():
            game = gs.single(gid)
            entry = [p for p in list(game["players"].values())
            if p["handle"] == player["handle"]][0]
            with table.tr as tr:
                tr(web.link('/game/', gid, "Game #%d" % gid))
                tr(web.link('/mode/', game["mode"],
                    redeclipse(game).modeimg(game["mode"])))
                tr(redeclipse(game).mutslist(game, True) or '-')
                tr(web.link("/map/", game["map"], game["map"], True))
                tr(timeutils.agohtml(game["time"]))
                tr(cgi.escape(entry["name"]))
                tr(redeclipse(game).scorestr(game, entry["score"]))
                tr(entry["frags"])
                tr(entry["deaths"])

        ret = """
        <div class="center">
            <h2><a href="/player/{player[handle]}">
            {player[handle]}</a>: Games</h2>
            <div class='display-table'>
                {table}
                {pages}
            </div>
        </div>
        """.format(player=player, table=table.html(), pages=pager.html())
    else:
        ret = "<div class='center'><h2>No such player.</h2></div>"
    return web.page(ret, title="%s: Games" % specific)