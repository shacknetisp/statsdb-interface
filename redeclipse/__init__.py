# -*- coding: utf-8 -*-
defaultversion = ""
from fnmatch import fnmatch
import importlib
cache = {}
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

    def __init__(self, db):
        self.db = db

    def __call__(self, gameid, mode):
        try:
            version = self.db.con.execute(
                "SELECT version FROM game_servers WHERE game = %d" % (
                    gameid)).fetchone()[0]
            return redeclipse(version).modes[mode]
        except:
            import traceback
            traceback.print_exc()


@functions.append
class sql_re_mut:

    numparams = 2
    name = "re_mut"

    def __init__(self, db):
        self.db = db

    def __call__(self, gameid, mode):
        try:
            version = self.db.con.execute(
                "SELECT version FROM game_servers WHERE game = %d" % (
                    gameid)).fetchone()[0]
            return redeclipse(version).mutators[mode]
        except:
            import traceback
            traceback.print_exc()