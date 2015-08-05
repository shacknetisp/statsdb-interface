# -*- coding: utf-8 -*-

#Red Eclipse Utilities
weaponlist = []
weapcols = ['timewielded', 'timeloadout']
for a in ['damage',
    'hits', 'shots',
    'flakhits', 'flakshots',
    'frags']:
        weapcols += [a + '1', a + '2']
m_laptime_sql = ("mode != 6 OR (mutators & 32768) = 0",
    "mode = 6 AND (mutators & 32768) != 0")
modestr = ["Demo", "Editing", "Deathmatch",
    "CTF", "DAC", "Bomber Ball", "Race"]


def scorestr(game, score):
    import timeutils
    if game["mode"] == 6 and game["mutators"] & 32768:
        return timeutils.durstr(score / 1000, dec=True)
    return str(score)


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
        {"key": "not-" + k, "sql": "%s NOT %s ?%s" % (s, c, e)}]


def mathfilter(k, s=None):
    if s is None:
        s = k
    return [
        {"key": k, "sql": "%s = ?" % (s)},
        {"key": "not-" + k, "sql": "%s NOT = ?" % (s)},
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

    def __init__(self):
        f = []
        for e in self.filters:
            if type(e) is list:
                f += e
            else:
                f.append(e)
        self.filters = f

    def makefilters(self):
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
        return (("WHERE " if sql else "") + " AND ".join(sql)), opts

    def copyfrom(self, other):
        self.pathid = other.pathid
        self.qopt = other.qopt
        self.server = other.server
        self.db = other.db

    def vlimit(self, i="game"):
        if "allversions" in self.qopt:
            return "1 = 1"
        return """%s IN (SELECT game FROM game_servers
        WHERE version GLOB '%s')""" % (i,
            self.server.cfgval("recordversion").replace("'", "''")
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
            gs = GameSelector()
            gs.copyfrom(self)
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
        boolfilter("timed", m_laptime_sql[1], m_laptime_sql[0]),
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
        ret["server"] = self.db.con.execute(
            """SELECT handle FROM game_servers
            WHERE game = %d""" % ret['id']).fetchone()[0]
        for team_row in self.db.con.execute(
            "SELECT * FROM game_teams WHERE game = %d" % row[0]):
                team = {}
                dictfromrow(team, team_row, [None, "team", "score", "name"])
                ret["teams"][team["name"]] = team
        for player_row in self.db.con.execute(
            "SELECT * FROM game_players WHERE game = %d" % row[0]):
                player = {
                    "weapons": {},
                    }
                dictfromrow(player, player_row, [None,
                    "name", "handle",
                    "score", "timealive", "frags", "deaths"])
                if one:
                    for weapon in weaponlist:
                        w = {}
                        for t in weapcols:
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
            for weapon in weaponlist:
                w = {}
                gameweapsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND game = %d""" % (
                        x, ret['id']),
                    (weapon,)).fetchone()[0]
                for t in weapcols:
                    w[t] = gameweapsum(t)
                ret['weapons'][weapon] = w
        return ret

    def getdict(self):
        if self.pathid is not None:
            return self.single(self.pathid)
        f = self.makefilters()
        ids = [r[0] for r in
        self.db.con.execute(
            """SELECT id FROM games
            %s""" % f[0], f[1])]
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
            gs = GameSelector()
            gs.copyfrom(self)
            game = gs.single(gid, one=False)
            ret["recentgames"][gid] = game
        #Data from games
        recentsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_players
            WHERE game IN (SELECT id FROM games WHERE %s)
            AND %s
            ORDER by ROWID DESC LIMIT %d)""" % (x,
            m_laptime_sql[0], self.vlimit(),
            self.server.cfgval("playerrecentavg"))
            ).fetchone()[0]
        allsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM game_players
            WHERE game IN (SELECT id FROM games WHERE %s)
            AND %s""" % (x,
                m_laptime_sql[0], self.vlimit())
            ).fetchone()[0]
        alltime = {
            'weapons': {},
            }
        recent = {
            'weapons': {},
            }
        for t in ['frags', 'deaths']:
            recent[t] = recentsum(t)
            alltime[t] = allsum(t)
        if one:
            #Weapon Data
            ##Individual Weapons
            for weapon in weaponlist:
                wr = {}
                wa = {}
                recentsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM
                    (SELECT * FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?
                    AND game IN (SELECT id FROM games WHERE %s)
                    AND %s
                    ORDER by ROWID DESC LIMIT %d)""" % (x, m_laptime_sql[0],
                    self.vlimit(),
                    self.server.cfgval("playerrecentavg")),
                    (weapon, ret['handle'])).fetchone()[0]
                allsum = lambda x: self.db.con.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?
                    AND %s
                    AND game IN (SELECT id FROM games WHERE %s)""" % (
                        x, self.vlimit(), m_laptime_sql[0]),
                    (weapon, ret['handle'])).fetchone()[0]
                for t in weapcols:
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
            %s""" % f[0], f[1])]
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
        wr = {}
        wa = {}
        recentsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_weapons WHERE weapon = ?
            AND %s
            ORDER by ROWID DESC LIMIT %d)""" % (x,
            self.vlimit(),
            self.server.cfgval("weaponrecentavg")),
            (name,)).fetchone()[0]
        allsum = lambda x: self.db.con.execute(
            """SELECT sum(%s) FROM game_weapons WHERE weapon = ?""" % (
                x),
            (name,)).fetchone()[0]
        for t in weapcols:
            wr[t] = recentsum(t)
            wa[t] = allsum(t)
        return {
            'recent': wr,
            'alltime': wa,
            }

    def getdict(self):
        if self.pathid is not None:
            if self.pathid not in weaponlist:
                return None
            return self.single(self.pathid)
        ret = {}
        for w in weaponlist:
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
            }
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT id FROM games
            WHERE map = ?""", (mapname,))]
        if one:
            for gid in list(reversed(ret["games"]))[
                :self.server.cfgval("maprecent")]:
                gs = GameSelector()
                gs.copyfrom(self)
                game = gs.single(gid, one=False)
                ret["recentgames"][gid] = game
        for row in self.db.con.execute(
            """SELECT id FROM games
            WHERE map = ?
            AND %s
            AND %s
            AND (mutators & 1024) = 0""" % (self.vlimit("id"),
                m_laptime_sql[1]), (mapname,)):
                gs = GameSelector()
                gs.copyfrom(self)
                game = gs.single(row[0], one=False)
                finishedplayers = [
                    p for p in game["players"] if p["score"] > 0]
                bestplayer = None
                for p in finishedplayers:
                    if not bestplayer or p["score"] <= bestplayer["score"]:
                        bestplayer = p
                if bestplayer:
                    if bestplayer["score"] <= ret[
                        "toprace"]["time"] or ret["toprace"]["time"] == 0:
                            ret["toprace"]["time"] = bestplayer["score"]
                            ret["toprace"]["gameplayer"] = bestplayer
                            ret["toprace"]["game"] = game

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
        except ValueError:
            return None
        ret = {
            "name": modestr[mint],
            "recentgames": {},
            }
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT id FROM games
            WHERE mode = ?""", (mode,))]
        if one:
            for gid in list(reversed(ret["games"]))[
                :self.server.cfgval("moderecent")]:
                gs = GameSelector()
                gs.copyfrom(self)
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
            ret[modes] = self.single(modes, False)
        return ret

selectors = {
    'servers': ServerSelector(),
    'games': GameSelector(),
    'players': PlayerSelector(),
    'weapons': WeaponSelector(),
    'maps': MapSelector(),
    'modes': ModeSelector(),
    }