# -*- coding: utf-8 -*-
import redeclipse


#Other Utilities
def dictfromrow(d, r, l, start=0):
    for i in range(len(l)):
        if l[i] is not None:
            d[l[i]] = r[i + start]


def boolfilter(k, s, nots):
    if s is None:
        s = k
    return [
        {"key": k, "sql": s},
        {"key": "not-" + k, "sql": nots}]


def basicfilter(k, c="=", s=None):
    if s is None:
        s = k
    e = ""
    return [
        {"key": k, "sql": "%s %s ?%s" % (s, c, e)},
        {"key": "not-" + k, "sql": "NOT %s %s ?%s" % (s, c, e)}]


def mathfilter(k, s=None):
    if s is None:
        s = k
    return [
        {"key": k, "sql": "%s = ?" % (s)},
        {"key": "not-" + k, "sql": "NOT %s = ?" % (s)},
        {"key": "lt-" + k, "sql": "%s < ?" % (s)},
        {"key": "gt-" + k, "sql": "%s > ?" % (s)}]


class basicxfilter:

    def __init__(self, k, t=None):
        self.k = k
        self.t = t if t is not None else k

    def __call__(self, sel, v):
        if sel.qopt[self.k] and v[self.t] not in sel.qopt[self.k]:
            return False
        if v[self.t] in sel.qopt["not-%s" % self.k]:
            return False
        return True


class BaseSelector:

    filters = []
    xfilters = []

    def __init__(self, sel=None, pathid=False):
        f = []
        for e in self.filters:
            if type(e) is list:
                f += e
            else:
                f.append(e)
        self.filters = f
        if sel is not None:
            self.copyfrom(sel)
            if not pathid:
                self.pathid = None

    def makefilters(self, where=True):
        sql = []
        opts = []
        for f in self.filters:
            if '?' in f["sql"]:
                if f['key'] in self.qopt:
                    sql.append(f["sql"])
                    opts.append(self.qopt(f['key']))
            else:
                if f['key'] in self.qopt:
                    sql.append(f["sql"])
        return (("WHERE " if sql and where else "") + " AND ".join(
            sql)), tuple(opts)

    def copyfrom(self, other):
        self.pathid = other.pathid
        self.qopt = other.qopt
        self.server = other.server
        self.db = other.db

    def vlimit(self, i="game"):
        if "allversions" in self.qopt:
            return "1 = 1"
        return """%s IN (SELECT game FROM game_servers
        WHERE %s)""" % (i,
            redeclipse.versions(),
            )


class ServerSelector(BaseSelector):

    filters = [
        basicfilter("host"),
        basicfilter("version", "GLOB"),
        basicfilter("flags", "GLOB"),
        ]

    def single(self, handle):
        ret = {
            "recentgames": {},
            }
        row = self.db.con.execute(
            """SELECT * FROM game_servers
            WHERE handle = ?
            ORDER BY ROWID DESC""", (handle,)).fetchone()
        if not row:
            return None
        dictfromrow(ret, row, [
            "handle", "flags", "desc", "version", "host", "port"
            ], start=1)
        if not ret['desc']:
            ret['desc'] = ret['host'] + ':' + str(ret['port'])
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT game FROM game_servers
            WHERE handle = ?""", (handle,))]
        for gid in list(reversed(ret["games"]))[
            :self.server.cfgval("serverrecent")]:
            gs = GameSelector(self)
            game = gs.single(gid, one=False)
            ret["recentgames"][gid] = game
        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters()
        handles = [r[0] for r in
        self.db.con.execute(
            """SELECT DISTINCT handle FROM game_servers
            %s""" % f[0], f[1])]
        ret = {}
        for handle in handles:
            ret[handle] = self.single(handle)
        return ret


class GameSelector(BaseSelector):

    filters = [
        basicfilter("mode"),
        mathfilter("time"),
        mathfilter("timeplayed"),
        boolfilter("timed",
            redeclipse.m_laptime_sql[1], redeclipse.m_laptime_sql[0]),
        ]
    xfilters = [
        basicxfilter("map"),
        ]

    def xfilter_players(self, v):
        handles = [p['handle'] for p in v["players"]]
        for handle in self.qopt["playerhandle"]:
            if handle not in handles:
                return False
        for handle in self.qopt["not-playerhandle"]:
            if handle in handles:
                return False
        return True
    xfilters.append(xfilter_players)

    def xfilter_mutators(self, v):
        if "mutator" in self.qopt:
            for mutator in self.qopt["mutator"]:
                try:
                    mutator = int(mutator)
                except:
                    return False
                if not (v["mutators"] & mutator):
                    return False
        for mutator in self.qopt["not-mutator"]:
            try:
                mutator = int(mutator)
            except:
                return False
            if v["mutators"] & mutator:
                return False
        return True
    xfilters.append(xfilter_mutators)

    def single(self, num, one=True):
        if not hasattr(self, 'minimal'):
            self.minimal = False
        row = self.db.con.execute(
            """SELECT * FROM games
            WHERE id = ?""", (num,)).fetchone()
        if not row:
            return None
        ret = {
            "teams": {},
            "players": [],
            "weapons": {},
            }
        dictfromrow(ret, row, ["id", "time",
            "map", "mode", "mutators",
            "timeplayed"])
        if self.minimal == "basic":
            return ret
        ret["server"] = self.db.con.execute(
            """SELECT handle FROM game_servers
            WHERE game = %d""" % ret['id']).fetchone()[0]
        # Minimal Sets
        if self.minimal == "basicserver":
            return ret
        if self.minimal in ["basicplayer", "basicplayer2"]:
            for player_row in self.db.con.execute(
                "SELECT * FROM game_players WHERE game = %d" % row[0]):
                    player = {}
                    dictfromrow(player, player_row, [None,
                        "name", "handle",
                        "score", "timealive", "frags", "deaths", "id"])
                    if self.minimal == 'basicplayer2':
                        player["damage"] = self.db.con.execute(
                            """SELECT (sum(damage1) + sum(damage2))
                            FROM game_weapons
                            WHERE game = %d AND player = %s""" % (
                                row[0], player["id"])).fetchone()[0]
                    ret["players"].append(player)
            return ret
        # Teams
        for team_row in self.db.con.execute(
            "SELECT * FROM game_teams WHERE game = %d" % row[0]):
                team = {}
                dictfromrow(team, team_row, [None, "team", "score", "name"])
                ret["teams"][team["name"]] = team
        #Affinities
        captures = []
        for capture_row in self.db.con.execute(
            "SELECT * FROM game_captures WHERE game = %d" % row[0]):
                capture = {}
                dictfromrow(capture, capture_row, [None,
                    "player", "playerhandle", "capturing", "captured"])
                captures.append(capture)
        if captures:
            ret['captures'] = captures
        bombings = []
        for bombing_row in self.db.con.execute(
            "SELECT * FROM game_bombings WHERE game = %d" % row[0]):
                bombing = {}
                dictfromrow(bombing, bombing_row, [None,
                    "player", "playerhandle", "bombing", "bombed"])
                bombings.append(bombing)
        if bombings:
            ret['bombings'] = bombings
        #Rounds
        if one:
            ffarounds = []
            for ffaround_row in self.db.con.execute(
                "SELECT * FROM game_ffarounds WHERE game = %d" % row[0]):
                    ffaround = {}
                    dictfromrow(ffaround, ffaround_row, [None,
                        "player", "playerhandle", "round", "winner"])
                    ffarounds.append(ffaround)
            if ffarounds:
                ret['ffarounds'] = ffarounds
        #Full Players
        for player_row in self.db.con.execute(
            "SELECT * FROM game_players WHERE game = %d" % row[0]):
                player = {
                    "weapons": {},
                    "captures": [],
                    "bombings": [],
                    }
                dictfromrow(player, player_row, [None,
                    "name", "handle",
                    "score", "timealive", "frags", "deaths", "id"])

                player["damage"] = self.db.con.execute(
                        """SELECT (sum(damage1) + sum(damage2))
                        FROM game_weapons
                        WHERE game = %d AND player = %s""" % (
                            row[0], player["id"])).fetchone()[0]

                for capture in captures:
                    if capture["player"] == player["id"]:
                        player["captures"].append(capture)

                for bombing in bombings:
                    if bombing["player"] == player["id"]:
                        player["bombings"].append(bombing)

                if one:
                    for weapon in redeclipse.weaponlist:
                        w = {'name': weapon}
                        for t in redeclipse.weapcols:
                            try:
                                w[t] = self.db.con.execute("""
                                SELECT %s FROM game_weapons
                                WHERE game = %d
                                AND player = %d AND weapon = ?""" % (
                                    t, ret['id'], player_row[7]
                                    ), (weapon,)).fetchone()[0]
                            except TypeError:
                                w[t] = 0
                        player["weapons"][weapon] = w
                ret["players"].append(player)
        if one:
            for weapon in redeclipse.weaponlist:
                w = {'name': weapon}
                gameweapsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND game = %d""" % (
                        x, ret['id']),
                    (weapon,)).fetchone()[0]
                for t in redeclipse.weapcols:
                    w[t] = gameweapsum(t)
                ret['weapons'][weapon] = w
        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters(where=False)
        if self.server.dbexists:
            ids = [r[0] for r in
            self.db.con.execute(
                """SELECT id FROM games
                WHERE %s AND %s""" % (self.gamefilter
                if hasattr(self, 'gamefilter') else '1 = 1',
                f[0] if f[0] else "1 = 1"), f[1])]
        else:
            ids = []
        if "recent" in self.qopt:
            ids = list(reversed(ids))[:self.server.cfgval("gamerecent")]
        ret = {}
        for gid in ids:
            v = self.single(gid, False)
            for f in self.xfilters:
                if v is not None:
                    if not f(self, v):
                        v = None
            if v is not None:
                ret[gid] = v
        return ret

    def numgames(self):
        if not self.server.dbexists:
            return 0
        return self.db.con.execute("SELECT count(id) FROM games").fetchone()[0]

    def getrid(self):
        if not self.server.dbexists:
            return []
        return [r[0] for r in self.db.con.execute("SELECT id FROM games")]


class PlayerSelector(BaseSelector):

    filters = [
        basicfilter("name", "GLOB"),
        ]

    def single(self, handle, one=True):
        row = self.db.con.execute(
            """SELECT * FROM game_players
            WHERE handle = ?
            ORDER BY ROWID DESC""", (handle,)).fetchone()
        if row is None:
            return None
        ret = {
            'handle': row[2],
            "recentgames": {},
            }
        dictfromrow(ret, row, [
            "name"
            ], start=1)
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT game FROM game_players
            WHERE handle = ?""", (handle,))]
        for gid in list(reversed(ret["games"]))[
            :self.server.cfgval("playerrecent")]:
            gs = GameSelector(self)
            game = gs.single(gid, one=False)
            ffarounds = []
            for ffaround_row in self.db.con.execute(
                """SELECT * FROM game_ffarounds
                WHERE playerhandle = ?
                AND game = %d""" % gid, (handle,)):
                    ffaround = {}
                    dictfromrow(ffaround, ffaround_row, ["game",
                        None, None, "round", "winner"])
                    ffarounds.append(ffaround)
            if ffarounds:
                game['player_ffarounds'] = ffarounds
            ret["recentgames"][gid] = game
        #Data from games
        recentsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_players
            WHERE game IN (SELECT id FROM games WHERE %s
            AND mode != {modes[race]})
            AND %s
            AND handle = ?
            ORDER by ROWID DESC LIMIT %d)""".format(
                modes=redeclipse.modes) % (x,
                redeclipse.m_laptime_sql[0],
                self.vlimit(),
                self.server.cfgval("playerrecentavg")), (handle,)).fetchone()[0]
        allsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM game_players
            WHERE game IN (SELECT id FROM games WHERE %s
            AND mode != {modes[race]})
            AND handle = ?
            AND %s""".format(
                modes=redeclipse.modes) % (x,
                redeclipse.m_laptime_sql[0],
                self.vlimit()), (handle,)
            ).fetchone()[0]
        alltime = {
            'weapons': {},
            }
        recent = {
            'weapons': {},
            }

        captures = []
        for capture_row in self.db.con.execute(
            "SELECT * FROM game_captures WHERE playerhandle = ?", (handle,)):
                capture = {}
                dictfromrow(capture, capture_row, ["game",
                    None, None, "capturing", "captured"])
                captures.append(capture)
        if captures:
            ret['captures'] = captures
        bombings = []
        for bombing_row in self.db.con.execute(
            "SELECT * FROM game_bombings WHERE playerhandle = ?", (handle,)):
                bombing = {}
                dictfromrow(bombing, bombing_row, ["game",
                    None, None, "bombing", "bombed"])
                bombings.append(bombing)
        if bombings:
            ret['bombings'] = bombings

        for t in ['frags', 'deaths', 'timealive']:
            recent[t] = recentsum(t)
            alltime[t] = allsum(t)

        recent["damage"] = self.db.con.execute(
            """SELECT (sum(damage1) + sum(damage2)) FROM game_weapons
                WHERE %s
                AND playerhandle = ?
                AND game IN (SELECT id FROM games WHERE mode != {modes[race]})
                ORDER by ROWID DESC LIMIT %d""".format(
                modes=redeclipse.modes) % (self.vlimit(),
                self.server.cfgval("playerrecentavg")),
                    (ret["handle"],)).fetchone()[0]

        alltime["damage"] = self.db.con.execute(
            """SELECT (sum(damage1) + sum(damage2)) FROM game_weapons
                WHERE %s
                AND game IN (SELECT id FROM games WHERE mode != {modes[race]})
                AND playerhandle = ?""".format(
                modes=redeclipse.modes) % (self.vlimit()),
                (ret["handle"],)).fetchone()[0]

        if one:
            #Weapon Data
            ##Individual Weapons
            for weapon in redeclipse.weaponlist:
                wr = {'name': weapon}
                wa = {'name': weapon}
                recentsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM
                    (SELECT * FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?
                    AND game IN (SELECT id FROM games WHERE %s)
                    AND %s
                    ORDER by ROWID DESC LIMIT %d)""" % (x,
                    redeclipse.m_laptime_sql[0],
                    self.vlimit(),
                    self.server.cfgval("playerrecentavg")),
                    (weapon, ret['handle'])).fetchone()[0]
                allsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?
                    AND %s
                    AND game IN (SELECT id FROM games WHERE %s)""" % (
                        x, self.vlimit(), redeclipse.m_laptime_sql[0]),
                    (weapon, ret['handle'])).fetchone()[0]
                for t in redeclipse.weapcols:
                    wr[t] = recentsum(t)
                    wa[t] = allsum(t)
                alltime['weapons'][weapon] = wa
                recent['weapons'][weapon] = wr
        ret["alltime"] = alltime
        ret["recent"] = recent
        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters()
        ids = [r[0] for r in
        self.db.con.execute(
            """SELECT DISTINCT handle FROM game_players
            %s""" % f[0], f[1]) if r[0]]
        ret = {}
        for gid in ids:
            v = self.single(gid, False)
            for f in self.xfilters:
                if v is not None:
                    if not f(self, v):
                        v = None
            if v is not None:
                ret[gid] = v
        return ret


class WeaponSelector(BaseSelector):

    def single(self, name):
        wr = {'name': name}
        wa = {'name': name}
        recentsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_weapons WHERE weapon = ?
            AND %s
            AND game IN (SELECT id FROM games WHERE %s)
            ORDER by ROWID DESC LIMIT %d)""" % (x,
            self.vlimit(),
            redeclipse.m_race_sql[0],
            self.server.cfgval("weaponrecentavg")),
            (name,)).fetchone()[0]
        allsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM game_weapons WHERE weapon = ?
            AND game IN (SELECT id FROM games WHERE %s)""" % (
                x, redeclipse.m_race_sql[0]),
            (name,)).fetchone()[0]
        for t in redeclipse.weapcols:
            wr[t] = recentsum(t) or 0
            wa[t] = allsum(t) or 0
        return {
            'recent': wr,
            'alltime': wa,
            }

    def getdict(self):
        if self.pathid is not None:
            if self.pathid not in redeclipse.weaponlist:
                return None
            return self.single(self.pathid)
        ret = {}
        for w in redeclipse.weaponlist:
            ret[w] = self.single(w)
        return ret


class MapSelector(BaseSelector):

    def single(self, mapname, one=True):
        ret = {
            "name": mapname,
            "recentgames": {},
            "toprace": {
                "game": None,
                "gameplayer": None,
                "time": 0,
                },
            "topraces": [],
            }
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT id FROM games
            WHERE map = ?""", (mapname,))]
        if not ret["games"]:
            return None
        if one:
            for gid in list(reversed(ret["games"]))[
                :self.server.cfgval("maprecent")]:
                gs = GameSelector(self)
                game = gs.single(gid, one=False)
                ret["recentgames"][gid] = game
        racetimes = []
        for row in self.db.con.execute(
            """SELECT id FROM games
            WHERE map = ?
            AND %s
            AND %s
            AND (mutators & 1024) = 0""" % (self.vlimit("id"),
                redeclipse.m_laptime_sql[1]), (mapname,)):
                gs = GameSelector(self)
                game = gs.single(row[0], one=False)
                finishedplayers = [
                    p for p in game["players"] if p["score"] > 0]
                for p in finishedplayers:
                    rtime = {}
                    rtime["time"] = p["score"]
                    rtime["gameplayer"] = p
                    rtime["game"] = game
                    racetimes.append(rtime)
        racetimes = sorted(racetimes, key=lambda x: x["time"])
        tmpracetimes = []
        handles = []
        for rtime in racetimes:
            if rtime["gameplayer"]["handle"] not in handles:
                tmpracetimes.append(rtime)
            if rtime["gameplayer"]["handle"]:
                handles.append(rtime["gameplayer"]["handle"])
        racetimes = tmpracetimes
        if racetimes:
            ret["toprace"] = racetimes[0]
        ret["topraces"] = racetimes[:10]
        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters()
        maps = [r[0] for r in
        self.db.con.execute(
            """SELECT DISTINCT map FROM games
            %s""" % f[0], f[1])]
        ret = {}
        for mapname in maps:
            ret[mapname] = self.single(mapname, False)
        return ret


class ModeSelector(BaseSelector):

    def single(self, mode, one=True):
        try:
            mint = int(mode)
        except TypeError:
            return None
        if mint not in list(range(len(redeclipse.modestr))):
            return None
        ret = {
            "id": mint,
            "name": redeclipse.modestr[mint],
            "recentgames": {},
            }
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT id FROM games
            WHERE mode = ?""", (mode,))]
        if one:
            for gid in list(reversed(ret["games"]))[
                :self.server.cfgval("moderecent")]:
                gs = GameSelector(self)
                game = gs.single(gid, one=False)
                ret["recentgames"][gid] = game

        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters()
        modes = [r[0] for r in
        self.db.con.execute(
            """SELECT DISTINCT mode FROM games
            %s""" % f[0], f[1])]
        ret = {}
        for mode in modes:
            ret[mode] = self.single(mode, False)
        return ret

selectors = {
    'servers': ServerSelector(),
    'games': GameSelector(),
    'players': PlayerSelector(),
    'weapons': WeaponSelector(),
    'maps': MapSelector(),
    'modes': ModeSelector(),
    }
