# -*- coding: utf-8 -*-
import web
import dbselectors
import timeutils
from redeclipse import redeclipse


def multi(request, db):
    gs = dbselectors.get('games', db)
    gs.flags_none()
    gs.weakflags(['server'], True)

    #Top Weapons
    ws = dbselectors.get('weapons', db, {'recentsums': [5000]})
    weapons = {}
    for name in redeclipse().loadoutweaponlist:
        weapon = ws.single(name)
        weapons[name] = weapon

    topweapons = {
        'wield': ('melee', 0),
        'dpm': ('melee', 0),
        'totalwielded': 0,
        }
    if weapons:
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            weapon[1]["damage1"]
            / (max(weapon[1]["timewielded"], 1) / 60) +
            weapon[1]["damage2"]
            / (max(weapon[1]["timewielded"], 1) / 60)))[0]
        topweapons['dpm'] = (best[0], (best[1]["damage1"]
            / (max(best[1]["timewielded"], 1) / 60) +
            best[1]["damage2"]
            / (max(best[1]["timewielded"], 1) / 60)))
        topweapons['totalwielded'] = sum([w['timewielded']
            for w in list(weapons.values())])
        best = sorted(list(weapons.items()), key=lambda weapon: -(
            max(weapon[1]["timewielded"], 1)))[0]
        topweapons['wield'] = (best[0], best[1]["timewielded"])

    # Recent Games
    gamestable = web.Table(
        ["ID", "Mode", "Mutators", "Server", "Map", "Duration", "Played"])
    games = gs.multi()
    for gid in sorted(list(games.keys()), reverse=True)[:10]:
        game = games[gid]
        with gamestable.tr as tr:
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
    <div class='display-table float-table'>
        <h5><a href="/weapons">Weapons</a></h5>
        <table>
            <tr>
                <td>Best DPM</td>
                <td>{weapdpm}</td>
            </tr>
            <tr>
                <td>Most Wielded</td>
                <td>{weapwield}</td>
            </tr>
        </table>
    </div>
    <div style="clear: both;"></div>
    <div class='display-table'>
        <h5><a href="/games">Latest Games</a></h5>
        <table>
            {games}
        </table>
    </div>
    <div style="clear: both;"></div>
    """.format(
        weapdpm="%s %s [%d DPM]" % (
            redeclipse().weaponimg(topweapons['dpm'][0]),
            web.link('/weapon/', topweapons['dpm'][0], topweapons['dpm'][0]),
            topweapons['dpm'][1]),
        weapwield="%s %s [%d%%]" % (
            redeclipse().weaponimg(topweapons['wield'][0]),
            web.link('/weapon/', topweapons['wield'][0],
                topweapons['wield'][0]),
            topweapons['wield'][1]
                / max(topweapons['totalwielded'], 1) * 100),
        games=gamestable.html(),
        )
    return web.page(ret, title="Overview")
