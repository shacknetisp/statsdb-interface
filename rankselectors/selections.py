# -*- coding: utf-8 -*-
import web
import dbselectors
import rankselectors
import time
from redeclipse import redeclipse


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Game selections: Last %d days" % self.days

    def update(self):
        gs = dbselectors.get('game', self.db,
            {'gt-time': [time.time() - 60 * 60 * 24 * self.days]})
        gs.flags_none()
        new = {}
        for game in list(gs.multi().values()):
            m = game["mode"]
            idx = (web.link('/mode/', m, redeclipse().modeimg(m)),
                redeclipse(game).mutslist(game, True, True) or '-')
            if idx not in new:
                new[idx] = 0
            new[idx] += 1
        with self.lock:
            self.data = new

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(["Mode", "Mutators", "Games"])
        if pager is not None:
            indexes = pager.list()
        else:
            indexes = sorted(data, key=lambda x: -data[x])[:limit]
        for m in indexes:
            with table.tr as tr:
                tr(m[0])
                tr(m[1])
                tr(data[m])
        return table

    def page(self, request):
        ret = """
        <a href="/ranks/modes/{days}">Single Modes</a>
        |
        <a href="/ranks/muts/{days}">Single Mutators</a>
        <div class='display-table small-table'>
            <h3>{title}</h3>
            {table}
        </div>
        """.format(table=self.table().html(),
            title=self.pagetitle, days=self.days)
        return web.page(ret, self.pagetitle)