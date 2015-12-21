# -*- coding: utf-8 -*-
import web
import dbselectors
import rankselectors
import time


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)

    def update(self):
        gs = dbselectors.get('game', self.db,
            {'gt-time': [time.time() - 60 * 60 * 24 * self.days]})
        gs.flags_none()
        gs.weakflags(['server'], True)
        new = {}
        for game in list(gs.multi().values()):
            if game["server"] not in new:
                new[game["server"]] = 0
            new[game["server"]] += 1
        with self.lock:
            self.data = new

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(["Name", "Games"])
        if pager is not None:
            indexes = pager.list()
        else:
            indexes = sorted(data, key=lambda x: -data[x])[:limit]
        ss = dbselectors.get('server', self.db)
        ss.flags_none()
        for s in indexes:
            with table.tr as tr:
                tr(web.link('/server/', s, ss.single(s)["desc"]))
                tr(data[s])
        return table
