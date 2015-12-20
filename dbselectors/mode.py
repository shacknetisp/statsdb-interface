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
        if specific in redeclipse().modes:
            mint = redeclipse().modes[specific]
        else:
            try:
                mint = int(specific)
            except TypeError:
                return {'Error': 'Mode does not exist'}
        if mint not in list(range(len(redeclipse().modestr))):
            return {}
        ret = {
            "id": mint,
            "name": redeclipse().modestr[mint],
            "corename": redeclipse().cmodestr[mint],
            "recentgames": {},
            }
        gamerows = list(self.db.execute(
            """SELECT * FROM games
            WHERE mode = re_mode(id, '%s')""" % ret["corename"]))
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
        for mode in list(redeclipse().modes.values()):
            ret[mode] = self.single(mode)
        return ret
