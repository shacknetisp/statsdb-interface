# -*- coding: utf-8 -*-
import dbselectors
import cfg


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = [
            "games", "recentgames"]
        super(Selector, self).__init__(*args, **kwargs)

    def fromrow(self, row):
        if not row:
            return {}
        ret = {
            "recentgames": {},
            }
        # Base
        dbselectors.rowtodict(ret, row, [
            "handle", "authflags", "desc", "version", "host", "port"
            ], start=1)
        if not ret['desc']:
            ret['desc'] = ret['host'] + ':' + str(ret['port'])
        # Game IDs
        if self.flags["games"]:
            gamerows = list(self.db.execute(
                """SELECT * FROM games
                WHERE id IN (SELECT id FROM game_servers WHERE handle = ?)""",
                (ret['handle'],)))
            ret["games"] = [r[0] for r in gamerows]
            # Game data
            if self.flags["recentgames"]:
                gs = dbselectors.get("game", self.db)
                gs.flags_none()
                gs.weakflags(['players'], True)
                for row in list(reversed(gamerows))[:cfg.get('recent')]:
                    game = gs.fromrow(row)
                    ret["recentgames"][game["id"]] = game
        return ret

    def make_single(self, specific):
        row = self.db.execute(
            """SELECT * FROM game_servers
            WHERE handle = ?
            ORDER BY ROWID DESC""", (specific,)).fetchone()
        return self.fromrow(row) or {'error': 'Does not exist.'}

    def make_multi(self):
        f = self.makefilters()
        handles = [r[0] for r in
        self.db.execute(
            """SELECT DISTINCT handle FROM game_servers
            %s""" % f[0], f[1])]
        ret = {}
        self.weakflags(['recentgames'], False)
        for handle in handles:
            ret[handle] = self.single(handle)
        return ret

    filters = [
        dbselectors.basicfilter("host"),
        dbselectors.basicfilter("version", "GLOB"),
        dbselectors.basicfilter("authflags", "GLOB"),
        ]
