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

# SQL Filters, [<is not>, <is>]
m_laptime_sql = ("mode != 6 OR (mutators & 32768) = 0",
    "mode = 6 AND (mutators & 32768) != 0")
m_race_sql = ("mode != 6",
    "mode = 6")

modestr = ["Demo", "Editing", "Deathmatch",
    "CTF", "DAC", "Bomber Ball", "Race"]


def scorestr(game, score):
    """Display score as a str, as time or points depending on the game."""
    import timeutils
    if game["mode"] == 6 and game["mutators"] & 32768:
        return timeutils.durstr(score / 1000, dec=True)
    return str(score)