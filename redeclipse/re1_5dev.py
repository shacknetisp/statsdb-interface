# -*- coding: utf-8 -*-
import cgi
from collections import OrderedDict
# Red Eclipse settings that may change in later releases.

# Weapon Lists
loadoutweaponlist = ["pistol", "sword", "shotgun",
    "smg", "flamer", "plasma", "zapper", "rifle"]
weaponlist = ["melee"] + loadoutweaponlist + ["grenade", "mine", "rocket"]

# Weapon Columns
weapcols = ['timewielded', 'timeloadout']
for a in ['damage',
    'hits', 'shots',
    'flakhits', 'flakshots',
    'frags']:
        weapcols += [a + '1', a + '2']

modes = {
    "dm": 2,
    "ctf": 3,
    "dac": 4,
    "bb": 5,
    "race": 6,
    }

cmodestr = {}
for k, v in list(modes.items()):
    cmodestr[v] = k


def tomuts(l, a=0):
    ret = OrderedDict()
    for i, mut in enumerate(l):
        ret[mut] = 1 << (i + a)
    return ret

#Mutators
mutators = {}
basemuts = ["multi", "ffa", "coop", "insta", "medieval", "kaboom",
    "duel", "survivor", "classic", "onslaught", "freestyle", "vampire",
    "resize", "hard", "basic", "gsp"]
gspmuts = {
    modes["ctf"]: ["quick", "defend", "protect"],
    modes["dac"]: ["quick", "king"],
    modes["bb"]: ["hold", "basket", "attack"],
    modes["race"]: ["marathon", "timed", "gauntlet"],
    }
gspnum = basemuts.index("gsp") - 1
basemuts = tomuts(basemuts)
del basemuts["gsp"]
mutators.update(basemuts)
for mode, modemuts in list(gspmuts.items()):
    modemuts = tomuts(modemuts, gspnum)
    gspmuts[mode] = modemuts
    mutators.update(modemuts)


def mutslist(game, html=False, short=False):
    muts = []

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    for m in basemuts:
        if (game["mutators"] & basemuts[m]):
            muts.append(m)

    if game['mode'] in gspmuts:
        for m in gspmuts[game['mode']]:
            if (game["mutators"] & gspmuts[game['mode']][m]):
                muts.append(m)
    if html:
        if short:
            out = []
            for m in muts:
                out.append(m)
            return cgi.escape('-'.join(out))
        outl = chunks(muts, 3)
        htmll = []
        for chunk in outl:
            htmll.append(cgi.escape(" ".join(chunk)))
        return "<br>".join(htmll)
    return muts

# SQL Filters, [<is not>, <is>]
m_laptime_sql = ("mode != %d OR (mutators & %d) = 0" % (modes["race"],
    mutators["timed"]),
    "mode = %d AND (mutators & %d) != 0" % (modes["race"],
    mutators["timed"]))
m_race_sql = ("mode != %d" % modes["race"],
    "mode = 6 %d" % modes["race"])

modestr = ["Demo", "Editing", "Deathmatch",
    "CTF", "DAC", "Bomber Ball", "Race"]


def scorestr(game, score):
    """Display score as a str, as time or points depending on the game."""
    import timeutils
    if game["mode"] == modes["race"] and game["mutators"] & mutators["timed"]:
        return timeutils.durstr(score / 1000, dec=True, full=True)
    return str(score)


def modeimg(mode, c=24):
    return '''<img class="img%d"
    title="%s" src="%s" alt="%s">''' % (c, modestr[mode],
        "/images/modes/%d.png" % mode,
        modestr[mode])


def weaponimg(weap, c=24):
    return '''<img class="img%d"
    title="%s" src="%s" alt="%s">''' % (c, weap,
        "/images/weapons/%s.png" % weap,
        weap)


def teamimg(t, c=24):
    return '''<img class="img%d"
    title="%s" src="%s" alt="%s">''' % (c, t,
        "/images/teams/%s.png" % t,
        t)