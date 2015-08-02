# -*- coding: utf-8 -*-


def dictfromrow(d, r, l, start=0):
    for i in range(len(l)):
        if l[i] is not None:
            d[l[i]] = r[i + start]


def equalsfilter(k, s=None):
    if s is None:
        s = k
    return {"key": k, "sql": "%s = ?" % s}


def likefilter(k, s=None):
    if s is None:
        s = k
    return {"key": k, "sql": "%s LIKE ?" % s}


class BaseSelector:

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
        equalsfilter("host"),
        likefilter("version"),
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


selectors = {
    'servers': ServerSelector(),
    }