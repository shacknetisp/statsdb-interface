# -*- coding: utf-8 -*-
import dbselectors
import utils
import cfg
from redeclipse import redeclipse


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = ["recentgames"]
        super(Selector, self).__init__(*args, **kwargs)

    def make_single(self, specific):
        if specific not in list(redeclipse().basemuts.keys()):
            return {'Error': 'Mut does not exist'}
        ret = {
            "id": specific,
            "recentgames": {},
            }
        gamerows = list(self.db.execute(
            """SELECT id FROM games
            WHERE mutators & re_mut(id, '%s')""" % ret["id"]))
        ret["games"] = [r[0] for r in gamerows]

        gs = dbselectors.get("game", self.db)
        gs.flags_none()
        gs.weakflags(['players'], True)

        # Recent Games
        if self.flags['recentgames']:
            num = self.q.qint('recentgames', cfg.get('recent'))
            for row in utils.sliceneg(list(reversed(gamerows)), num):
                game = gs.fromrow(row)
                ret["recentgames"][game["id"]] = game

        return ret

    def make_multi(self):
        ret = {}
        self.weakflags(['recentgames'], False)
        for mut in list(redeclipse().basemuts.keys()):
            ret[mut] = self.single(mut)
        return ret