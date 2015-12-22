# -*- coding: utf-8 -*-
import dbselectors
import web
from redeclipse import redeclipse
import timeutils
import utils
import cgi
onpagecount = 15
recentlimit = 500


def single(request, db, specific):
    playerselector = dbselectors.get('player', db, {'recentsums': [-1]})
    playerselector.flags_none()
    playerselector.weakflags(
        ['games', 'damage', 'recentgames', 'recentsums', 'weapons'], True)

    recentplayerselector = dbselectors.get('player', db,
        {'recentsums': [recentlimit]})
    recentplayerselector.flags_none()
    recentplayerselector.weakflags(
        ['games', 'damage', 'recentsums', 'weapons'], True)

    gameselector = dbselectors.get('game', db)
    gameselector.flags_none()

    player = playerselector.single(specific)
    recentplayer = recentplayerselector.single(specific)
    if utils.sok(player) and utils.sok(recentplayer):
        #Top map
        topmap = "-"
        maps = {}
        for row in db.execute('''SELECT map FROM games
            WHERE id IN (SELECT game
            FROM game_players WHERE handle = ?
            ORDER by ROWID DESC LIMIT %d)''' % recentlimit,
                (player["handle"],)):
                    if row[0] not in maps:
                        maps[row[0]] = 0
                    maps[row[0]] += 1
        if maps:
            t = sorted(maps, key=lambda x: -maps[x])[0]
            topmap = web.link('/map/', t, t)
        # Play time
        timeplayed = timeutils.durstr(player["recent"]["timeactive"],
            skip="s", skiplow=False, full=True)
        #DPM
        try:
            dpm = "%d" % (round(player["recent"]["damage"]
                / (player["recent"]["timealive"] / 60)))
        except TypeError:
            dpm = "-"
        #Frag ratio
        try:
            fratio = "%.2f [%d / %d]" % ((player["recent"]["frags"] /
                max(1, player["recent"]["deaths"])),
                    player["recent"]["frags"],
                    player["recent"]["deaths"])
        except TypeError:
            fratio = "-"
        #Recent Games
        gamestable = web.Table(["Game", "Mode", "Mutators",
            "Map", "Time", "Played As", "Score", "Frags", "Deaths"])
        for gid in sorted(
            list(player["recentgames"].keys()), reverse=True)[:5]:
                game = player["recentgames"][gid]
                entry = game["player"]
                with gamestable.tr as tr:
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
        #Weapons
        totalwielded = sum([w['timewielded']
            for w in list(recentplayer['recent']['weapons'].values())
            if w['timewielded'] is not None])
        weaponstable = web.displays.weaponstable(
            recentplayer['recent']['weapons'],
            totalwielded, redeclipse().weaponlist)
        ret = """
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
                {games}
                <h5 style="text-align: left;">
                <a href="/playergames/{player[handle]}">
                All Games...</a></h5>
            </div>
            <div class='display-table small-table'>
                <h3>Weapon Statistics: Last {recentnum} games.</h3>
                {weapons}
            </div>
        </div>
        """.format(
            player=player,
            firstago=web.link("/game/", player["games"][0],
                timeutils.agohtml(
                    gameselector.single(player["games"][0])["time"])),
            lastago=web.link("/game/", player["games"][-1],
                timeutils.agohtml(
                    gameselector.single(player["games"][-1])["time"])),
            topmap=topmap,
            timeplayed=timeplayed,
            dpm=dpm,
            fratio=fratio,
            games=gamestable.html(),
            weapons=weaponstable.html(),
            recentnum=recentlimit,
            )
    else:
        ret = "<div class='center'><h2>No such player.</h2></div>"
    return web.page(ret, title="Player %s" % specific)


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