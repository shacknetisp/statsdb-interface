# -*- coding: utf-8 -*-
import importlib
import cfg
import time
from threading import Lock
import copy

cache = {}
alloweddays = [7, 30, 90, 180, 365]

#List of selectors
#(<api calling points>, <rank selector module>)
selectors = [
    (['maps'], 'maps'),
    (['servers'], 'servers'),
    (['spm'], 'spm'),
    (['dpm'], 'dpm'),
    (['fpm'], 'fpm'),
    (['spf'], 'spf'),
    (['weapon'], 'weapon'),
    (['games'], 'games'),
    (['captures'], 'captures'),
    (['bombings'], 'bombings'),
    (['mvp'], 'mvp'),
    (['winners'], 'winners'),
]


class Selector:

    def __init__(self, db, days, opts):
        self.db = db
        self.days = days
        self.data = {}
        self.lock = Lock()
        self.opts = opts

    def get(self):
        with self.lock:
            return copy.deepcopy(self.data)


def importselector(s):
    c = importlib.import_module("rankselectors." + s).Selector
    c.name = s
    return c

ns = {}
for s in selectors:
    for an in s[0]:
        ns[an] = importselector(s[1])
selectors = ns


def get(selector, db, days, opts=None):
    index = str([selector, days, opts])
    if index in cache:
        return cache[index][1]
    s = selectors[selector](db, days, opts or {})
    cache[index] = [time.time(), s]
    s.update()
    return s


def tick(db):
    for index in cache:
        if time.time() - cache[index][0] > cfg.get('cache_ranks'):
            with db:
                cache[index][0] = time.time()
                cache[index][1].db = db
                cache[index][1].update()
