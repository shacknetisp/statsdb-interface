# -*- coding: utf-8 -*-
from . import base
import api
import dbselectors
import caches
import redeclipse
from .base import tdlink, alink
import timeutils
from . import pt


def page(sel):
    recentgames = ""
    gs = dbselectors.GameSelector()
    gs.copyfrom(sel)
    gs.pathid = None
    gs.qopt = api.Qopt({
        "recent": [True],
        })
    games = gs.getdict()
    for gid, game in list(reversed(list(games.items())))[:10]:
        recentgames += '<tr>'
        recentgames += tdlink("game", gid, "Game #%d" % gid)
        recentgames += tdlink("mode",
            game["mode"],
            redeclipse.modeimg(game["mode"]), e=False)
        ss = dbselectors.ServerSelector()
        ss.copyfrom(sel)
        desc = ss.single(game["server"])["desc"]
        recentgames += tdlink('server', game["server"], desc)
        recentgames += tdlink('map', game["map"], game["map"])
        recentgames += '<td>%s</td>' % timeutils.durstr(round(
            game["timeplayed"]))
        recentgames += '<td>%s</td>' % timeutils.agohtml(game["time"])
        recentgames += '</tr>'

    ws = dbselectors.WeaponSelector()
    ws.copyfrom(sel)
    ws.pathid = None

    weapons = {}
    for name in redeclipse.loadoutweaponlist:
        weapon = ws.single(name)["recent"]
        weapons[name] = weapon

    topweapons = {}
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

    ptcounters = {
        "score": pt.gamelist(caches.caches["plsingle"].get("score", 7), num=5),
        "captures": pt.gamelist(caches.caches["plsingle"].get(
            "captures", 7), num=5),
        "bombings": pt.gamelist(caches.caches["plsingle"].get(
            "bombings", 7), num=5),
        "dpm": pt.gamedivlist(*caches.caches["spm"].get("dpm", 30), num=5),
        "spm": pt.gamedivlist(*caches.caches["spm"].get("spm", 30), num=5),
        "fpm": pt.gamedivlist(*caches.caches["spm"].get("fpm", 30), num=5),
        "maps": pt.mapnum(sel, 90),
        "servers": pt.servernum(sel, 90),
        }
    ret = """
    <h2>Recent Overview</h2>
    <h5><a href="/display/players">Players</a></h5>
    <h3>Last 7 Days</h3>
    <div class='display-table float-table'>
        <h5>Score</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Score</th>
            </tr>
            {ptcounters[score]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5>Captures</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Captures</th>
            </tr>
            {ptcounters[captures]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5>Bombings</h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Bombings</th>
            </tr>
            {ptcounters[bombings]}
        </table>
    </div>
    <div style="clear: both;"></div>
    <h3>Last 30 Days</h3>
    <div class='display-table float-table'>
        <h5><a href="/display/ranks/spm"
        title="Score Per Minute">SPM</a></h5>
        <table>
            <tr>
                <th>Name</th>
                <th>SPM</th>
            </tr>
            {ptcounters[spm]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5><a href="/display/ranks/dpm"
        title="Damage Per Minute">DPM</a></h5>
        <table>
            <tr>
                <th>Name</th>
                <th>DPM</th>
            </tr>
            {ptcounters[dpm]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5><a href="/display/ranks/fpm"
        title="Frags Per Minute">FPM</a></h5>
        <table>
            <tr>
                <th>Name</th>
                <th>FPM</th>
            </tr>
            {ptcounters[fpm]}
        </table>
    </div>
    <div style="clear: both;"></div>
    <h3>Last 90 Days</h3>
    <div class='display-table float-table'>
        <h5><a href="/display/maps">Maps</a></h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Games</th>
            </tr>
            {ptcounters[maps]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5><a href="/display/servers">Servers</a></h5>
        <table>
            <tr>
                <th>Name</th>
                <th>Games</th>
            </tr>
            {ptcounters[servers]}
        </table>
    </div>
    <div class='display-table float-table'>
        <h5><a href="/display/weapons">Weapons</a></h5>
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
        <h5><a href="/display/games">Latest Games</a></h5>
        <table>
            <tr>
                <th>ID</th>
                <th>Mode</th>
                <th>Server</th>
                <th>Map</th>
                <th>Duration</th>
                <th>Played</th>
            </tr>
            {recentgames}
        </table>
    </div>
    <div style="clear: both;"></div>
    """.format(recentgames=recentgames,
        ptcounters=ptcounters,
        topweapon="\n".join(topweapons),
        weapdpm="%s %s [%d DPM]" % (redeclipse.weaponimg(topweapons['dpm'][0]),
            alink('weapon', topweapons['dpm'][0], topweapons['dpm'][0]),
            topweapons['dpm'][1]),
        weapwield="%s %s [%d%%]" % (
            redeclipse.weaponimg(topweapons['wield'][0]),
            alink('weapon', topweapons['wield'][0], topweapons['wield'][0]),
            topweapons['wield'][1]
                / max(topweapons['totalwielded'], 1) * 100))
    return base.page(sel, ret, title="Overview")
