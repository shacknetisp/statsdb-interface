# -*- coding: utf-8 -*-
import dbselectors
from redeclipse import redeclipse


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = []
        super(Selector, self).__init__(*args, **kwargs)

    def make_single(self, specific):
        if specific not in redeclipse().weaponlist:
            return {"error": "Weapon not found"}
        ret = {'name': specific}
        recentsum = lambda x: self.db.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_weapons WHERE weapon = ?
            AND %s
            AND game IN (SELECT id FROM games WHERE mode != re_mode(id, 'race')
            AND (mutators & re_mut(id, 'insta')) = 0
            AND (mutators & re_mut(id, 'medieval')) = 0
            )
            %s)""" % (x,
            self.vlimit(),
            self.recent("recentsums")),
            (specific,)).fetchone()[0]
        for t in redeclipse().weapcols:
            ret[t] = recentsum(t) or 0
        return ret

    def make_multi(self):
        ret = {}
        for w in redeclipse().weaponlist:
            ret[w] = self.single(w)
        return ret
