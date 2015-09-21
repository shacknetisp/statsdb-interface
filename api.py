# -*- coding: utf-8 -*-
import json
import time
import dbselectors
import web


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Qopt:

    def __init__(self, q):
        self.q = q

    def __call__(self, opt, d=None, c=str):
        try:
            return c(self.q[opt][0])
        except:
            return d

    def __getitem__(self, opt):
        return self.q[opt] if opt in self.q else []

    def __contains__(self, key):
        return key in self.q


def counterwait(c):
    while not c.lastcache:
        time.sleep(1)


def make(server, db, q, path):

    if path in server.retcache:
        return server.retcache[path][1]

    def sendout(t):
        if path not in server.retcache:
            server.retcache[path] = (time.time(), t)
        return t

    qopt = Qopt(q)
    paths = path.split('/')[1:]
    sel = dbselectors.BaseSelector()
    sel.pathid = None
    sel.server = server
    sel.db = db
    sel.qopt = qopt
    if paths[0] == 'get':
        ret = {"error": "Invalid Query"}
        if not server.dbexists:
            return 'application/json', '200 OK', json.dumps(
                {"error": "Empty Database"}).encode()
        if len(paths) >= 2:
            name = paths[1]
            pathid = paths[2] if len(paths) >= 3 else None
            sel.pathid = pathid
            if name in dbselectors.selectors:
                dbselectors.selectors[name].copyfrom(sel)
                ret = dbselectors.selectors[name].getdict()
                if ret is None:
                    ret = {"error": "Invalid Query"}
        return sendout(('application/json', '200 OK', json.dumps(
            ret).encode()))
    elif paths[0] == 'display':
        if server.dbexists:
            if len(paths) >= 2:
                name = paths[1]
                pathid = paths[2] if len(paths) >= 3 else None
                sel.pathid = pathid
                if name in web.displays.displays:
                    ret = web.displays.displays[name](sel)
                    return sendout(('text/html', '200 OK', ret.encode()))
    elif paths[0] == 'images':
        try:
            return sendout(('image/png', '200 OK', open(
                "web/images/%s" % '/'.join(paths[1:]).replace(
                    '..', ''), 'rb').read()))
        except IndexError:
            pass
        except FileNotFoundError:
            pass
    elif paths[0] == 'styles':
        try:
            return sendout(('text/css', '200 OK', open(
                "web/styles/%s" % '/'.join(paths[1:]).replace(
                    '..', '')).read().encode()))
        except IndexError:
            pass
        except FileNotFoundError:
            pass
    elif not paths[0]:
        return sendout(('text/html', '200 OK', web.main.page(sel).encode()))
    elif paths[0] == 'apidocs':
        return sendout((('redirect',
        'https://github.com/shacknetisp/statsdb-interface#api-points'),))
    return sendout((
        'text/html', '404 Not Found', web.err404.page(sel).encode()))
