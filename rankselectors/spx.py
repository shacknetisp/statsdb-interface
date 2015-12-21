# -*- coding: utf-8 -*-
# Score per X
import web
import dbselectors
import rankselectors
import time


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.tabletitle = (None, None)
        self.playerkey = None
        self.divby = lambda x: x['timealive'] / 60
        self.rounddigits = 1
        self.sortkey = lambda x: -x[1]
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = ""
        self.q = {
            'fighting': [],
        }

    def update(self):
        self.q.update({
            'gt-time': [time.time() - 60 * 60 * 24 * self.days],
            'gt-uniqueplayers': [1],
        })
        gs = dbselectors.get('game', self.db, self.q)
        gs.flags_none()
        gs.weakflags(['players', 'playerdamage'], True)
        players = {}
        d = {}
        for game in list(gs.multi().values()):
            for player in list(game["players"].values()):
                if player["handle"]:
                    if player["handle"] not in players:
                        players[player["handle"]] = 0
                    players[player["handle"]] += self.playerkey(player)
                    if player["handle"] not in d:
                        d[player["handle"]] = 0
                    d[player["handle"]] += self.divby(player)
        for p in players:
            players[p] /= max(1, d[p])
            if self.rounddigits:
                players[p] = round(players[p], self.rounddigits)
            else:
                players[p] = round(players[p])
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
                tr(web.link('/player/', p[0], p[0]))
                tr(p[1])
        return table

    def page(self, request):
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
