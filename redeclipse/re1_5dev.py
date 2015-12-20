# -*- coding: utf-8 -*-
from . import default


# Red Eclipse settings that may change.
#Version 1.5.4+
class RE(default.RE):
    # Weapon Lists
    loadoutweaponlist = ["pistol", "sword", "shotgun",
        "smg", "flamer", "plasma", "zapper", "rifle"]
    weaponlist = ["melee"] + loadoutweaponlist + ["grenade", "mine", "rocket"]

    #Mode Lists
    modes = {
        "dm": 2,
        "ctf": 3,
        "dac": 4,
        "bb": 5,
        "race": 6,
        }

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

    #Fancy Mode Names
    modestr = ["Demo", "Editing", "Deathmatch",
        "CTF", "DAC", "Bomber Ball", "Race"]
