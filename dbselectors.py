# -*- coding: utf-8 -*-

#Red Eclipse Utilities
weaponlist = []
weapcols = ['timewielded', 'timeloadout']
for a in ['damage',
    'hits', 'shots',
    'flakhits', 'flakshots',
    'frags']:
        weapcols += [a + '1', a + '2']


#Other Utilities
def dictfromrow(d, r, l, start=0):
    for i in range(len(l)):
        if l[i] is not None:
            d[l[i]] = r[i + start]


def basicfilter(k, c="=", s=None):
    if s is None:
        s = k
    return [
        {"key": k, "sql": "%s %s ?" % (s, c)},
        {"key": "not-" + k, "sql": "%s NOT %s ?" % (s, c)}]


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
            if f['key'] in self.qopt:
                sql.append(f["sql"])
                opts.append(self.qopt(f['key']))
        return (("WHERE " if sql else "") + " AND ".join(sql)), opts


class ServerSelector(BaseSelector):

    filters = [
        basicfilter("host"),
        basicfilter("version", "LIKE"),
        basicfilter("flags", "LIKE"),
        ]

    def single(self, handle):
        ret = {}
        row = self.db.con.execute(
            """SELECT * FROM game_servers
            WHERE handle = ?
            ORDER BY ROWID DESC""", (handle,)).fetchone()
        if not row:
            return None
        dictfromrow(ret, row, [
            "handle", "flags", "desc", "version", "host", "port"
            ], start=1)
        ret["games"] = [r[0] for r in
        self.db.con.execute(
            """SELECT game FROM game_servers
            WHERE handle = ?""", (handle,))]
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
            WHERE id = %d""" % num).fetchone()
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
                            w[t] = self.db.con.execute("""
                            SELECT %s FROM game_weapons
                            WHERE game = %d
                            AND player = %d AND weapon = ?""" % (
                                t, ret['id'], player_row[7]
                                ), (weapon,)).fetchone()[0]
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


selectors = {
    'servers': ServerSelector(),
    'games': GameSelector(),
    }