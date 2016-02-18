# -*- coding: utf-8 -*-
import importlib
import cfg
import utils
cache = {}
fcache = {
    "mode": {},
    "mut": {},
    }
vcache = {}
functions = []
defaultversion = cfg.get("defaultversion")


def redeclipse(s=None):
    if s is None:
        s = {"version": defaultversion}
    if type(s) is str:
        s = {"version": s}
    if s["version"] in cache:
        return cache[s["version"]]
    version = utils.version(s["version"])
    for m, v in list(cfg.get('versions').items()):
        if (version >= utils.version(v[0]) and version <= utils.version(v[1])):
            cache[s["version"]] = importlib.import_module(
                "redeclipse.re%s" % m).RE()
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

sql_re_mut_modecache = {}


@functions.append
class sql_re_mut:

    numparams = 2
    name = "re_mut"

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


@functions.append
class sql_re_mut_check:

    numparams = 2
    name = "re_mut_check"

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
            if gameid in sql_re_mut_modecache:
                mode = sql_re_mut_modecache[gameid]
            else:
                mode = self.db.con.execute(
                    "SELECT mode FROM games WHERE id = %d" % (
                        gameid)).fetchone()[0]
                sql_re_mut_modecache[gameid] = mode
            fcache["mut"][(gameid, mut)] = 0
            if (mut in redeclipse(version).gspmuts[mode] or
                mut in redeclipse(version).basemuts):
                fcache["mut"][(gameid, mut)] = redeclipse(version).mutators[mut]
            return fcache["mut"][(gameid, mut)]
        except:
            import traceback
            traceback.print_exc()
            raise


@functions.append
class sql_re_verin:

    numparams = 3
    name = "re_verin"

    def __init__(self, db):
        self.db = db

    def __call__(self, version, lower, upper):
        try:
            version = utils.version(version)
            lower = utils.version(lower)
            upper = utils.version(upper)
            return (version >= lower and version <= upper)
        except:
            import traceback
            traceback.print_exc()
            raise
