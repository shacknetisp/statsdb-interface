# -*- coding: utf-8 -*-
import importlib
import web
import cgi
from redeclipse import redeclipse


#List of displays
#(<web calling points>, <display module>)
displays = [
    #(['', 'overview'], 'overview'),
    (['game', 'games', 'g'], 'game'),
    (['server', 'servers', 's'], 'server'),
    #(['player', 'players', 'p'], 'player'),
    #(['weapon', 'weapons'], 'weapon'),
    (['map', 'maps'], 'map'),
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


def weaponstable(weapons, totalwielded, order):
    table = web.Table(
        ["Weapon", "Loadout", "Wielded",
            '<abbr title="Damage Per Minute">DPM</abbr>',
            '<abbr title="Frags Per Minute">FPM</abbr>'],
                'Weapons', 'display-table small-table')
    for weapon in order:
        with table.tr as tr:
            weapon = weapons[weapon]
            weap = weapon["name"]
            tr(web.link("/weapon/", weap,
                '%s %s' % (redeclipse().weaponimg(weap), weap)))
            tr("%d%%" % (
                weapon["timeloadout"] / max(1, totalwielded) * 100))
            tr("%d%%" % (
                weapon["timewielded"] / max(1, totalwielded) * 100))
            psdiv = (weapon["timeloadout"]
                if weap == "melee"
                else weapon["timewielded"])
            psdiv = max(psdiv, 1)
            tr("<span class='explain' title='%d %d'>%d</span>" % (
                weapon["damage1"] / (psdiv / 60),
                weapon["damage2"] / (psdiv / 60),
                (weapon["damage1"] + weapon["damage2"]) / (
                    psdiv / 60)))
            tr("<span class='explain' title='%d %d'>%d</span></td>" % (
                weapon["frags1"] / (psdiv / 60),
                weapon["frags2"] / (psdiv / 60),
                (weapon["frags1"] + weapon["frags2"]) / (
                    psdiv / 60)))
    return table


def weapontable(weapon, totalwielded):
    return weaponstable({'a': weapon}, totalwielded, ['a'])
