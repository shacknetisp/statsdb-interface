# -*- coding: utf-8 -*-
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
    "race": 6,
    }
mutators = {
    "duel": 64,
    "survivor": 128,
    "timed": 32768,
    }

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
        return timeutils.durstr(score / 1000, dec=True)
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