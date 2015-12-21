# -*- coding: utf-8 -*-
import web
import dbselectors
import rankselectors
import time
from redeclipse import redeclipse


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Modes: Last %d days" % self.days

    def update(self):
        gs = dbselectors.get('game', self.db,
            {'gt-time': [time.time() - 60 * 60 * 24 * self.days]})
        gs.flags_none()
        new = {}
        for game in list(gs.multi().values()):
            if game["mode"] not in new:
                new[game["mode"]] = 0
            new[game["mode"]] += 1
        with self.lock:
            self.data = new

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(["Mode", "Games"])
        if pager is not None:
            indexes = pager.list()
        else:
            indexes = sorted(data, key=lambda x: -data[x])[:limit]
        for m in indexes:
            with table.tr as tr:
                tr(web.link('/mode/', m, redeclipse().modeimg(m)))
                tr(data[m])
        return table

    def page(self, request):
        ret = """
        <div class='display-table small-table'>
            <h3>{title}</h3>
            {table}
        </div>
        """.format(table=self.table().html(),
            title=self.pagetitle)
        return web.page(ret, self.pagetitle)
