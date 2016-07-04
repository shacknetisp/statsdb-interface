# -*- coding: utf-8 -*-
# Simple Sums
import web
import dbselectors
import rankselectors
import time


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.tabletitle = (None, None)
        self.playerkey = None
        self.uniqueplayers = 0
        self.sortkey = lambda x: -x[1]
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = ""
        self.q = {}
        self.extraflags = []

    def update(self):
        self.q.update({
            'gt-time': [time.time() - 60 * 60 * 24 * self.days],
            'gt-uniqueplayers': [self.uniqueplayers - 1],
        })
        gs = dbselectors.get('game', self.db, self.q)
        gs.flags_none()
        gs.weakflags(['players', 'playerdamage'] + self.extraflags, True)
        players = {}
        for game in list(gs.multi().values()):
            for player in list(game["players"].values()):
                if player["handle"]:
                    if player["handle"] not in players:
                        players[player["handle"]] = 0
                    players[player["handle"]] += self.playerkey(player)
        with self.lock:
            self.data = sorted(list(players.items()), key=self.sortkey)

    def table(self, limit=5, pager=None):
        data = self.get()
        table = web.Table(list(self.tabletitle))
        if pager is not None:
            indexes = pager.list()
        else:
            indexes = data[:limit]
        for p in indexes:
            with table.tr as tr:
                if p[1]:
                    tr(web.link('/player/', p[0], p[0]))
                    tr(p[1])
        return table

    def page(self, request):
        data = [x for x in self.get() if x[1] > 0]
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
