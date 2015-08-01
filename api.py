# -*- coding: utf-8 -*-
import json
import matplotlib
matplotlib.use('Agg')
import pylab as p
import time


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def qopt(q, opt, d=None):
    try:
        return q[opt][0]
    except:
        return d


def counterwait(c):
    while not c.lastcache:
        time.sleep(1)


def make(server, db, q, path):
    if path == '/get':
        name = qopt(q, 'q')
        arg = qopt(q, 'id')
        if name:
            return 'application/json', '200 OK', json.dumps(
                server.getdict(name, arg)).encode()
    return 'text/html', '400 NotFound', b'400 Not Found'
