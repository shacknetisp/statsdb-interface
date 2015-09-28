# -*- coding: utf-8 -*-
defaultversion = ""
from fnmatch import fnmatch
import importlib
cache = {}
fcache = {
    "mode": {},
    "mut": {},
    }
vcache = {}
functions = []


def redeclipse(s=None):
    if s is None:
        s = {"version": defaultversion}
    if type(s) is str:
        s = {"version": s}
    if s["version"] in cache:
        return cache[s["version"]]
    for m, v in list({
        "1_5dev": ["1.5.4"],
        }.items()):
            for match in v:
                if fnmatch(s["version"], match):
                    cache[s["version"]] = importlib.import_module(
                        "redeclipse.re%s" % m)
                    return cache[s["version"]]
    return None


@functions.append
class sql_re_mode:

    numparams = 2
    name = "re_mode"
    cache = {}

    def __init__(self, db):
        self.db = db

    def __call__(self, gameid, mode):
        try:
            if (gameid, mode) in fcache["mode"]:
                return fcache["mode"][(gameid, mode)]
            if gameid in vcache:
                version = vcache[gameid]
            else:
                version = self.db.con.execute(
                    "SELECT version FROM game_servers WHERE game = %d" % (
                        gameid)).fetchone()[0]
                vcache[gameid] = version
            fcache["mode"][(gameid, mode)] = redeclipse(version).modes[mode]
            return fcache["mode"][(gameid, mode)]
        except:
            import traceback
            traceback.print_exc()
            raise


@functions.append
class sql_re_mut:

    numparams = 2
    name = "re_mut"
    cache = {}

    def __init__(self, db):
        self.db = db

    def __call__(self, gameid, mut):
        try:
            if (gameid, mut) in fcache["mut"]:
                return fcache["mut"][(gameid, mut)]
            if gameid in vcache:
                version = vcache[gameid]
            else:
                version = self.db.con.execute(
                    "SELECT version FROM game_servers WHERE game = %d" % (
                        gameid)).fetchone()[0]
                vcache[gameid] = version
            fcache["mut"][(gameid, mut)] = redeclipse(version).mutators[mut]
            return fcache["mut"][(gameid, mut)]
        except:
            import traceback
            traceback.print_exc()
            raise