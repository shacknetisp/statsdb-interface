# -*- coding: utf-8 -*-
# Simple Sums
import web
import dbselectors
import rankselectors
import time


titles = {
    'ffa': 'FFA',
    'ffasurv': 'FFA Survivor',
}


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.tabletitle = ("Player", "Ratio")
        self.uniqueplayers = 2
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "%s win ratio: Last %d days" % (
            titles[str(self.opts)]
            if str(self.opts) in titles else "", self.days)
        self.q = {}

    def update(self):
        self.q.update({
            'gt-time': [time.time() - 60 * 60 * 24 * self.days],
            'gt-uniqueplayers': [self.uniqueplayers - 1],
            str(self.opts): [],
        })
        gs = dbselectors.get('game', self.db, self.q)
        gs.flags_none()
        gs.weakflags(['players'], True)
        players = {}
        for game in list(gs.multi().values()):
            plist = list(game["players"].values())
            best = sorted(plist, key=lambda x: -x["score"])[0]["score"]
            for player in plist:
                if player["handle"]:
                    if player["handle"] not in players:
                        players[player["handle"]] = [0, 0]
                    if player["score"] >= best:
                        players[player["handle"]][0] += 1
                    else:
                        players[player["handle"]][1] += 1
        with self.lock:
            self.data = sorted(list(players.items()),
                key=lambda x: -(x[1][0] / max(x[1][1], 1)))

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(list(self.tabletitle))
        if pager is not None:
            indexes = pager.list()
        else:
            indexes = data[:limit]
        for p in indexes:
            with table.tr as tr:
                tr(web.link('/player/', p[0], p[0]))
                tr("%d [%d/%d]" % (p[1][0] / max(1, p[1][1]), p[1][0], p[1][1]))
        return table

    def page(self, request):
        if str(self.opts) not in titles:
            return False
        data = self.get()
        pager = web.Pager(request, 10, data)
        ret = """
        <div class='display-table'>
            <h3>{title}</h3>
            {table}
            {pager}
        </div>
        """.format(table=self.table(pager=pager).html(),
            pager=pager.html(), title=self.pagetitle)
        return web.page(ret, self.pagetitle)
