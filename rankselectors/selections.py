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
            idx = (game["mode"], game["mutators"], game["version"])
            if idx not in new:
                new[idx] = 0
            new[idx] += 1
        with self.lock:
            self.data = new

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(['<a href="/ranks/modes/%d">Mode</a>' % self.days,
            '<a href="/ranks/muts/%d">Mutators</a>' % self.days, "Games"])
        if pager is not None:
            indexes = pager.list()
        else:
            if limit is not None:
                indexes = sorted(data, key=lambda x: -data[x])[:limit]
            else:
                indexes = sorted(data, key=lambda x: -data[x])
        for m in indexes:
            with table.tr as tr:
                fakegame = {
                    "mode": m[0],
                    "mutators": m[1],
                    "version": m[2],
                }
                tr(web.link('/mode/', m[0],
                    redeclipse(fakegame).modeimg(m[0])))
                tr(redeclipse(fakegame).mutslist(
                    fakegame, True, True) or '-')
                tr(data[m])
        return table

    def apiget(self):
        r = {}
        for k, v in list(self.data.items()):
            if k[0] not in r:
                r[k[0]] = {}
            r[k[0]][k[1]] = v
        return r

    def page(self, request):
        data = self.get()
        pager = web.Pager(request, 20, sorted(data, key=lambda x: -data[x]))
        ret = """
        <div class='display-table'>
            <h3>{title}</h3>
            {table}
            {pager}
        </div>
        """.format(table=self.table(pager=pager).html(),
            pager=pager.html(), title=self.pagetitle)
        return web.page(ret, self.pagetitle)