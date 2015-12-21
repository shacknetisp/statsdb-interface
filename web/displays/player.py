# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
onpagecount = 20


def multi(request, db):
    playerselector = dbselectors.get('player', db)
    playerselector.flags_none()
    playerselector.weakflags(['games'], True)

    gameselector = dbselectors.get('game', db)
    gameselector.flags_none()

    players = playerselector.multi()
    pager = web.Pager(request, onpagecount,
        sorted(players, key=lambda x: -players[x]["games"][-1]))
    playertable = web.Table(
        ["Name", "Handle", "Games", "First Game", "Latest Game"])
    for handle in pager.list():
        player = players[handle]
        firstgame = gameselector.single(player["games"][0])
        latestgame = gameselector.single(player["games"][-1])
        with playertable.tr as tr:
            tr(web.linkif('/player/', player["handle"], player["name"], True))
            tr(web.linkif('/player/', player["handle"], player["handle"], True))
            tr(len(player["games"]))
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
        <h2>Players</h2>
        <div class='display-table'>
            {playertable}
            {pages}
        </div>
    </div>
    """.format(playertable=playertable.html(), pages=pager.html())
    return web.page(ret, title="Players")