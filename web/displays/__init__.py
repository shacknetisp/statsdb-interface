# -*- coding: utf-8 -*-
import importlib
import web
from redeclipse import redeclipse


#List of displays
#(<web calling points>, <display module>)
displays = [
    (['', 'overview'], 'overview'),
    (['game', 'games', 'g'], 'game'),
    (['server', 'servers', 's'], 'server'),
    (['player', 'players', 'p'], 'player'),
    (['playergames'], 'playergames'),
    (['weapon', 'weapons'], 'weapon'),
    (['map', 'maps'], 'map'),
    (['racemaps'], 'racemaps'),
    (['mode', 'modes'], 'mode'),
    (['mut', 'mutator', 'muts', 'mutators'], 'mut'),
]


def importdisplay(s):
    c = importlib.import_module("web.displays." + s)
    return c

nd = {}
for d in displays:
    for an in d[0]:
        nd[an] = importdisplay(d[1])
displays = nd


def weaponstable(weapons, totalwielded, order, games=None, version=None):
    title = "Weapons"
    if len(order) == 1:
        title = weapons[order[0]]["name"].capitalize()
    if games is not None:
        title = "%s: Last %d games" % (title, games)
    table = web.Table(
        ["Weapon", "Loadout", "Wielded",
            '<abbr title="Damage Per Minute Wielded">DPM</abbr>',
            '<abbr title="Frags Per Minute Wielded">FPM</abbr>'],
                title, 'display-table small-table')
    for weapon in order:
        with table.tr as tr:
            weapon = weapons[weapon]
            if weapon["timeloadout"] is None:
                continue
            weap = weapon["name"]
            tr(web.link("/weapon/", weap,
                '%s %s' % (redeclipse().weaponimg(weap), weap)))
            tr("%d%%" % (
                weapon["timeloadout"] / max(1, totalwielded) * 100))
            nw = redeclipse(version).notwielded
            if (weap + '1') in nw and (weap + '2') in nw:
                tr("-")
            else:
                tr("%d%%" % (
                    weapon["timewielded"] / max(1, totalwielded) * 100))
            psdiv = max(weapon["timeloadout"]
                if (weap + '1') in nw else weapon["timewielded"], 1) / 60
            psdiv2 = max(weapon["timeloadout"]
                if (weap + '2') in nw else weapon["timewielded"], 1) / 60
            tr("<span class='explain' title='%d %d'>%d</span>" % (
                weapon["damage1"] / psdiv,
                weapon["damage2"] / psdiv2,
                weapon["damage1"] / psdiv + weapon["damage2"] / psdiv2))
            tr("<span class='explain' title='%.1f %.1f'>%.1f</span></td>" % (
                round(weapon["frags1"] / psdiv, 1),
                round(weapon["frags2"] / psdiv2, 1),
                round(weapon["frags1"] / psdiv + weapon["frags2"] / psdiv2, 1)
                ))
    return table


def weapontable(weapon, totalwielded, games=None, version=None):
    return weaponstable({'a': weapon}, totalwielded, ['a'], games, version)
