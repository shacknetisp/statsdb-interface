#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import db
import json
import sys
import select
from datetime import datetime
from wsgiref.simple_server import make_server, WSGIRequestHandler
from threading import Thread, Lock
import api
import urllib.parse
import time
import os
import traceback
import web
import dbselectors
import caches
import redeclipse

if len(sys.argv) < 2:
    print("Usage: python3 server.py <master server home directory>")
    sys.exit(1)

homedir = sys.argv[1]
os.makedirs(homedir + '/statsdbbackups', exist_ok=True)

try:
    config = json.loads(open(homedir + '/statsserver.json').read())
except FileNotFoundError:
    config = {}
defaultconfig = json.loads(open('defaultconfig.json').read())


def cfgval(key):
    if key in config:
        return config[key]
    return defaultconfig[key]

redeclipse.defaultversion = cfgval("defaultversion")


class httpd:

    def __init__(self, server):
        self.server = server

    def __call__(self, environ, start_response):
        sys.stdout.write(((datetime.now().strftime('%D %T')
        + ': ' + environ['REMOTE_ADDR']
        + ': ' + environ['PATH_INFO'] + '?' + environ['QUERY_STRING']).strip()
        + '...'))
        result = b""
        t = time.time()
        self.server.starttime = t
        try:
            r = api.make(self.server,
                self.server.db, urllib.parse.parse_qs(
                        environ['QUERY_STRING'], True), environ['PATH_INFO'])
        except:
            r = (
            'text/html',
            '500 Internal Server Error',
            web.err500.page(dbselectors.BaseSelector()).encode())
            print((traceback.format_exc()))
        sys.stdout.write('...done [%f]\n' % (time.time() - t))
        if len(r) == 3:
            t, status, result = r
            headers = [('Content-type', '%s' % t)]
        elif len(r) == 2:
            t = r[0]
            args = r[1:]
            if t == 'redirect':
                status = "301 Moved Permanently"
                headers = [('Location', '%s' % args[0])]
        start_response(status, headers)
        return [result]


class httphandler (WSGIRequestHandler):

    def log_message(self, format, *args):
        pass


class Server:

    def __init__(self):
        self.lasttick = 0
        self.retcache = {}
        self.path = homedir + '/stats.sqlite'
        self.db = db.DB(self.path)
        self.dblock = Lock()
        self.httpd = make_server(cfgval("host"), cfgval("port"),
            httpd(self),
            handler_class=httphandler)
        sel = dbselectors.BaseSelector()
        sel.pathid = None
        sel.server = self
        sel.db = self.db
        sel.qopt = api.Qopt({})
        caches.make(sel)
        self.tick()
        thread = Thread(target=Server.do_http, args=(self, ))
        thread.setDaemon(True)
        thread.start()
        self.starttime = 0
        with self.dblock:
            with self.db:
                api.make(self,
                        self.db, {}, "/")
        print("Created initial cache, server running.")

    def do_http(self):
        while True:
            if select.select([self.httpd], [], [], 3)[0]:
                with self.dblock:
                    with self.db:
                        self.httpd.handle_request()

    def tick(self):
        #Calculate caches
        with self.db:
            for c in caches.classes:
                c[0].calcall()
        #Clear old cached pages
        todel = []
        for k, v in list(self.retcache.items()):
            dt = 5
            if v[1][0] in ['text/html', 'text/json']:
                dt = 1
            if time.time() - v[0] >= 60 * dt:
                todel.append(k)
        for k in todel:
            del self.retcache[k]
        if time.time() - self.lasttick >= 60 * 1:
            self.lasttick = time.time()
            #Determine if the database exists
            with self.db:
                self.dbexists = self.db.con.execute(
                        "PRAGMA table_info(games)").fetchone(
                            ) is not None
                if self.dbexists:
                    self.dbexists = self.db.con.execute(
                        "SELECT id FROM games ORDER BY id DESC").fetchone(
                            ) is not None
            #Create a backup, remove old backups
            backupfile = (homedir +
            "/statsdbbackups/" +
            time.strftime("%Y%m%d") + '.sqlite.bak')
            if not os.path.exists(backupfile):
                self.db.backup(backupfile)
                print("Creating backup.")
            db.flushdir(homedir + "/statsdbbackups",
                60 * 60 * 24 * cfgval("backupkeepdays"))

    def cfgval(self, k):
        return cfgval(k)

server = Server()
while True:
    with server.dblock:
        server.tick()
    time.sleep(1)