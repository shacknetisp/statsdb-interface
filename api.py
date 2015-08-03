# -*- coding: utf-8 -*-
import json
import time
import dbselectors


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
    qopt = Qopt(q)
    paths = path.split('/')[1:]
    if paths[0] == 'get':
        if not server.dbexists:
            return 'application/json', '200 OK', json.dumps(
                {}).encode()
        if len(paths) >= 2:
            name = paths[1]
            pathid = paths[2] if len(paths) >= 3 else None
            if name in dbselectors.selectors:
                dbselectors.selectors[name].pathid = pathid
                dbselectors.selectors[name].server = server
                dbselectors.selectors[name].db = db
                dbselectors.selectors[name].qopt = qopt
                ret = dbselectors.selectors[name].getdict()
                if ret is None:
                    ret = {"error": "Invalid Query"}
                return 'application/json', '200 OK', json.dumps(
                    ret).encode()
    return 'text/html', '404 NotFound', b'404 Not Found'
