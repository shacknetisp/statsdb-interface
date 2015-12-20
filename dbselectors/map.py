# -*- coding: utf-8 -*-
import dbselectors
import utils
import cfg


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = ["recentgames", "race"]
        super(Selector, self).__init__(*args, **kwargs)

    def make_single(self, specific):
        ret = {
            "name": specific,
            "recentgames": {},
            "toprace": {
                "game": None,
                "gameplayer": None,
                "time": 0,
                },
            "topraces": [],
            }
        gamerows = list(self.db.execute(
            """SELECT * FROM games
            WHERE map = ?""", (ret['name'],)))
        ret["games"] = [r[0] for r in gamerows]
        if not ret["games"]:
            return {'error': 'Map has no games'}
        gs = dbselectors.get("game", self.db)
        gs.flags_none()
        gs.weakflags(['players'], True)

        # Recent Games
        if self.flags['recentgames']:
            num = self.q.qint('recentgames', cfg.get('recent'))
            for row in utils.sliceneg(list(reversed(gamerows)), num):
                game = gs.fromrow(row)
                ret["recentgames"][game["id"]] = game

        # Race Times
        if self.flags['race']:
            racetimes = []
            for row in self.db.execute(
                """SELECT * FROM games
                WHERE map = ?
                AND mode = re_mode(id, 'race')
                AND(mutators & re_mut(id, 'timed'))
                AND %s
                AND (mutators & re_mut(id, 'freestyle')) = 0""" % (
                    self.vlimit("id")), (ret['name'],)):
                    game = gs.fromrow(row)
                    finishedplayers = [
                        p for p in list(game["players"].values())
                        if p["score"] > 0]
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

    def make_multi(self):
        ret = {}
        f = self.makefilters()
        maps = [r[0] for r in
        self.db.execute(
            """SELECT DISTINCT map FROM games
            %s""" % f[0], f[1])]
        self.weakflags(['recentgames', 'race'], False, True)
        for mapname in maps:
            ret[mapname] = self.single(mapname)
        return ret
