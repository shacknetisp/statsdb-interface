# -*- coding: utf-8 -*-
# Weapons
import web
import dbselectors
import rankselectors
import time


class Selector(rankselectors.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.q = {
            'gt-time': [time.time() - 60 * 60 * 24 * self.days],
            'gt-uniqueplayers': [0],
            'fighting': [],
        }
        self.weapon = self.opts["weapon"]

    def update(self):
        gs = dbselectors.get('game', self.db, self.q)
        gs.flags_none()
        gs.weakflags(['players', 'playerweapons'], True)
        players = {}
        d = {}
        key = self.weapon
        for game in list(gs.multi().values()):
            for p in list(game["players"].values()):
                if p['handle']:
                    if p['handle'] not in players:
                        players[p['handle']] = 0
                    if p['handle'] not in d:
                        d[p['handle']] = 0
                    d[p['handle']] += p['timealive'] / 60
                    if key[0] in p['weapons']:
                        if key[1] == 0:
                            players[p['handle']] += (
                                p['weapons'][key[0]]['damage1']
                                + p['weapons'][key[0]]['damage2']
                                + ((p['weapons'][key[0]]['frags1']
                                + p['weapons'][key[0]]['frags2']) * 100))
                        else:
                            players[p['handle']] += (
                                p['weapons'][key[0]]['damage%d' % key[1]]
                                + ((p['weapons'][key[0]][
                                    'frags%d' % key[1]]) * 100))
        for p in players:
            players[p] /= max(1, d[p])
            players[p] = round(players[p])
        with self.lock:
            self.data = sorted(list(players.items()), key=lambda x: -x[1])

    def best(self):
        data = self.get()
        if not data:
            return "<i>Nobody</i>"
        return web.link('/player/', data[0][0], data[0][0])
