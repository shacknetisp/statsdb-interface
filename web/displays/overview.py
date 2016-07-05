# -*- coding: utf-8 -*-
import web
import dbselectors
import timeutils
import rankselectors
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
        'wield': (redeclipse().weaponlist[0], 0),
        'dpm': (redeclipse().weaponlist[0], 0),
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
            tr("%s [%s]" % (
                web.link('/server/', game["server"], game["server"]),
                game["version"]))
            tr(web.link('/map/', game["map"], game["map"], True))
            tr(timeutils.durstr(round(game["timeplayed"])))
            tr(timeutils.agohtml(game["time"]))

    ranks = {
        "spf": rankselectors.get('spf', db, 7).table().html(),
        "captures": rankselectors.get('captures', db, 7).table().html(),
        "bombings": rankselectors.get('bombings', db, 7).table().html(),
        "affmvp": rankselectors.get('mvp', db, 7, "affmvp").table().html(),
        "dmmvp": rankselectors.get('mvp', db, 7, "dmmvp").table().html(),
        "sword": rankselectors.get('weapon', db, 7,
            {"weapon": ('sword', 0)}).best(),
        "sniper": rankselectors.get('weapon', db, 7,
            {"weapon": ('rifle', 2)}).best(),

        "spm": rankselectors.get('spm', db, 30).table().html(),
        "dpm": rankselectors.get('dpm', db, 30).table().html(),
        "fpm": rankselectors.get('fpm', db, 30).table().html(),
        "games": rankselectors.get('games', db, 30).table().html(),

        "maps": rankselectors.get('maps', db, 90).table().html(),
        "servers": rankselectors.get('servers', db, 90).table().html(),
        "ffa": rankselectors.get(
            'winners', db, 90, 'ffa').table().html(),
        "ffasurv": rankselectors.get(
            'winners', db, 90, 'ffasurv').table().html(),
    }

    ret = """
    <h2>Recent Overview</h2>

    <h5><a href="/players">Players</a></h5>
    <h3>Last 7 Days</h3>
    <div class='display-table float-table'>
        <h5>Score/Frags</h5>
        {ranks[spf]}
    </div>
    <div class='display-table float-table'>
        <h5>
        <span class="explain" title="Most Flag Captures">Captures</span></h5>
        {ranks[captures]}
    </div>
    <div class='display-table float-table'>
        <h5>
        <span class="explain" title="Most Base Bombings">Bombings</span></h5>
        {ranks[bombings]}
    </div>
    <div class='display-table float-table'>
        <h5><span class="explain"
        title="Scores from CTF and BB">CTF/BB Team Scores</span></h5>
        {ranks[affmvp]}
    </div>
    <div class='display-table float-table'>
        <h5><span class="explain"
        title="Scores from DM">DM Team Scores</span></h5>
        {ranks[dmmvp]}
    </div>
    <div class='display-table float-table'>
        <h5>Best</h5>
        <table>
            <tr>
                <td><span class="explain"
title="Best Damage and Frags with the Sword">Knight</span></td>
                <td>{ranks[sword]}</td>
            </tr>
            <tr>
                <td><span class="explain"
title="Best Damage and Frags with the Rifle Secondary">
Sniper</span></td>
                <td>{ranks[sniper]}</td>
            </tr>
        </table>
    </div>

    <div style="clear: both;"></div>
    <h3>Last 30 Days</h3>
    <div class='display-table float-table'>
        <h5><a href="/ranks/spm/180"
            class="explain" title="Score per Minute">SPM</a></h5>
        {ranks[spm]}
    </div>
    <div class='display-table float-table'>
        <h5><a href="/ranks/dpm/180"
            class="explain" title="Damage per Minute">DPM</a></h5>
        {ranks[dpm]}
    </div>
    <div class='display-table float-table'>
        <h5><a href="/ranks/fpm/180"
            class="explain" title="Frags per Minute">FPM</a></h5>
        {ranks[fpm]}
    </div>
    <div class='display-table float-table'>
        <h5><a href="/ranks/games/365">Games</a></h5>
        {ranks[games]}
    </div>

    <div style="clear: both;"></div>
    <h3>Last 90 Days</h3>
    <div class='display-table float-table'>
        <h5><a href="/maps">Maps</a></h5>
        {ranks[maps]}
    </div>
    <div class='display-table float-table'>
        <h5><a href="/servers">Servers</a></h5>
        {ranks[servers]}
    </div>
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
    <div class='display-table float-table'>
        <h5><a href="/ranks/winners/180?opts=ffa">
        FFA Win Ratio</a></h5>
        {ranks[ffa]}
    </div>
    <div class='display-table float-table'>
        <h5><a href="/ranks/winners/180?&opts=ffasurv">
        FFA Survivor Win Ratio</a></h5>
        {ranks[ffasurv]}
    </div>

    <div style="clear: both;"></div>
    <div class='display-table'>
        <h5><a href="/games">Latest Games</a></h5>
        {games}
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
        ranks=ranks,
        )
    return web.page(ret, title="Overview")
