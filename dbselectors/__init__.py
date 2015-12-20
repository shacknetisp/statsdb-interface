# -*- coding: utf-8 -*-
import importlib
import collections
import time
import cfg
import utils

cache = {}

#List of selectors
#(<api calling points>, <db selector module>)
selectors = [
    (['game', 'games'], 'game'),
    (['server', 'servers'], 'server'),
    (['player', 'players'], 'player'),
    (['weapon', 'weapons'], 'weapon'),
    (['map', 'maps'], 'map'),
    (['mode', 'modes'], 'mode'),
    (['mut', 'mutator', 'muts', 'mutators'], 'mut'),
]


class QOpt(collections.defaultdict):

    def __init__(self, *args, **kwargs):
        super(QOpt, self).__init__(*args, **kwargs)

    def qstr(self, v, d=""):
        if v in self and self[v]:
            return self[v][0]
        return d

    def qint(self, v, d=0):
        return utils.toint(self.qstr(v), d)


class Selector:

    filters = []
    xfilters = []

    def __init__(self, q, db, specific):
        self.db = db
        self.q = QOpt(lambda: list())
        self.q.update(q)
        self.specific = specific

        self.weakflagged = {}

        # Build flag list
        nf = {}
        for f in self.flags:
            if type(f) is str:
                nf[f] = True
            else:
                nf[f[0]] = f[1]
        self.flags = nf
        # Enable or disable all flags
        if 'all-flags' in self.q:
            self.flags_all()
        if 'clear-flags' in self.q:
            self.flags_none()
        # Specific Flags
        if 'no-flags' in self.q:
            for f in self.q['no-flags']:
                self.flags[f] = False
        if 'flags' in self.q:
            for f in self.q['flags']:
                self.flags[f] = True

        # Build filter list
        f = []
        for e in self.filters:
            if type(e) is list:
                f += e
            else:
                f.append(e)
        self.filters = f

    def makefilters(self, where=True):
        sql = []
        opts = []
        for f in self.filters:
            if '?' in f["sql"]:
                if f['key'] in self.q:
                    sql.append(f["sql"])
                    v = self.q[f['key']][0] if self.q[f['key']] else None
                    opts.append(v)
            else:
                if f['key'] in self.q:
                    sql.append(f["sql"])
        return (("WHERE " if sql and where else "") + " AND ".join(
            sql)), tuple(opts)

    def flags_none(self):
        for k in self.flags:
            self.flags[k] = False

    def flags_all(self):
        for k in self.flags:
            self.flags[k] = True

    # Only set these flags if they are not specified
    def weakflags(self, flags, value, very=False):
        for flag in flags:
            if very and flag in self.weakflagged:
                continue
            if 'flags' in self.q and flag in self.q['flags']:
                continue
            if 'no-flags' in self.q and flag in self.q['no-flags']:
                continue
            self.flags[flag] = value
            if not very:
                self.weakflagged[flag] = True

    # Handle caching of single
    def single(self, specific=None):
        specific = self.specific if specific is None else specific
        index = str([self.name, 'single',
            list(self.q.items()), self.flags, specific])
        if index not in cache or (
            time.time() - cache[index][0] > cfg.get('cache_selectors')):
                cache[index] = (time.time(), self.make_single(specific))
        return cache[index][1]

    # Handle caching of multi
    def multi(self):
        index = str([self.name, 'multi', list(self.q.items()), self.flags])
        if index not in cache or (
            time.time() - cache[index][0] > cfg.get('cache_selectors')):
                cache[index] = (time.time(), self.make_multi())
        return cache[index][1]

    #Version limit (massive weapon changes, etc)
    def vlimit(self, i="game"):
        if "no-vlimit" in self.q:
            return "1 = 1"
        return """%s IN (SELECT game FROM game_servers
        WHERE %s)""" % (i,
            ' OR version GLOB '.join(['1 = 0'] + [
                ("'%s'" % x) for x in cfg.get('countversions')]),
            )

    #Recent param, < 0 means no limit.
    def recent(self, k):
        num = self.q.qint(k, cfg.get('recent'))
        if num < 0:
            return ""
        return "ORDER by ROWID DESC LIMIT %d" % (num)


def rowtodict(d, r, l, start=0):
    for i in range(len(l)):
        if l[i] is not None:
            d[l[i]] = r[i + start]


def boolfilter(k, s, nots):
    if s is None:
        s = k
    return [
        {"key": k, "sql": s},
        {"key": "not-" + k, "sql": nots}]


def basicfilter(k, c="=", s=None):
    if s is None:
        s = k
    e = ""
    return [
        {"key": k, "sql": "%s %s ?%s" % (s, c, e)},
        {"key": "not-" + k, "sql": "NOT %s %s ?%s" % (s, c, e)}]


def mathfilter(k, s=None):
    if s is None:
        s = k
    return [
        {"key": k, "sql": "%s = ?" % (s)},
        {"key": "not-" + k, "sql": "NOT %s = ?" % (s)},
        {"key": "lt-" + k, "sql": "%s < ?" % (s)},
        {"key": "gt-" + k, "sql": "%s > ?" % (s)}]


class basicxfilter:

    def __init__(self, k, t=None):
        self.k = k
        self.t = t if t is not None else k

    def __call__(self, sel, v):
        if sel.q[self.k] and v[self.t] not in sel.q[self.k]:
            return False
        if v[self.t] in sel.q["not-%s" % self.k]:
            return False
        return True


def importselector(s):
    c = importlib.import_module("dbselectors." + s).Selector
    c.name = s
    return c

ns = {}
for s in selectors:
    for an in s[0]:
        ns[an] = importselector(s[1])
selectors = ns


def get(selector, db, q=None):
    s = selectors[selector](q or {}, db, None)
    return s
