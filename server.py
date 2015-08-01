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

if len(sys.argv) < 2:
    print("Usage: python3 server.py <master server home directory>")
    sys.exit(1)

homedir = sys.argv[1]
os.makedirs(homedir + '/statsdbbackups', exist_ok=True)

config = json.loads(open(homedir + '/statsserver.json').read())


class httpd:

    def __init__(self, server):
        self.server = server

    def __call__(self, environ, start_response):
        print(((datetime.now().strftime('%D %T')
        + ': ' + environ['REMOTE_ADDR']
        + ': ' + environ['PATH_INFO'] + '?' + environ['QUERY_STRING']).strip()))
        t, status, result = api.make(self.server,
            self.server.db, urllib.parse.parse_qs(
                    environ['QUERY_STRING'], True), environ['PATH_INFO'])
        headers = [('Content-type', '%s' % t)]
        start_response(status, headers)
        return [result]


class httphandler (WSGIRequestHandler):

    def log_message(self, format, *args):
        pass


def dictfromrow(d, r, l, start):
    for i in range(len(l)):
        d[l[i]] = r[i + start]


class Server:

    def __init__(self):
        self.lasttick = 0
        self.path = homedir + '/stats.sqlite'
        self.cachelock = Lock()
        self.cache = None
        self.db = db.DB(self.path)
        self.httpd = make_server(config['host'], config['port'],
            httpd(self),
            handler_class=httphandler)
        self.tick()
        thread = Thread(target=Server.do_http, args=(self, ))
        thread.setDaemon(True)
        thread.start()
        print("Web server running.")

    def do_http(self):
        while True:
            if self.cache and select.select([self.httpd], [], [], 3)[0]:
                self.httpd.handle_request()

    def tick(self):
        if time.time() - self.lasttick > 30:
            self.lasttick = time.time()
            print(('[%s] Caching...' % (datetime.now().strftime('%D %T'))))
            self.tcache = {
                "servers": {}
                }
            with self.db:
                #Servers
                sc = {}
                for row in self.db.con.execute(
                    "SELECT DISTINCT handle FROM game_servers"):
                        server = {
                            "handle": row[0],
                            }
                        lastrow = self.db.con.execute(
                            """SELECT * FROM game_servers
                            WHERE handle = ?
                            ORDER BY ROWID DESC""", (row[0],)).fetchone()
                        dictfromrow(server, lastrow, [
                            "flags", "desc", "version", "host", "port"
                            ], start=2)
                        server["games"] = [r[0] for r in
                        self.db.con.execute(
                            """SELECT game FROM game_servers
                            WHERE handle = ?""", (row[0],))]
                        sc[row[0]] = server
                self.tcache["servers"] = sc
            with self.cachelock:
                self.cache = self.tcache
            print("...Cached")

            backupfile = (homedir +
            "/statsdbbackups/" +
            "statsdb" +
            time.strftime(".%Y%m%d"))
            if not os.path.exists(backupfile):
                self.db.backup(backupfile)
            db.flushdir(homedir + "/statsdbbackups", 60 * 60 * 24 * 30)

    def getdict(self, name, query):
        inverr = {'error': "Invalid Query"}
        nferr = {'error': "Not Found"}
        with self.cachelock:
            if name == "server":
                if query:
                    if query not in self.cache["servers"]:
                        return nferr
                    return self.cache["servers"][query]
                return self.cache["servers"]
            else:
                return inverr

server = Server()
while True:
    server.tick()
    time.sleep(1)