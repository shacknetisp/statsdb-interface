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
import cache

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


class Server:

    def __init__(self):
        self.lasttick = 0
        self.path = homedir + '/stats.sqlite'
        self.cachelock = Lock()
        self.cache = None
        self.db = db.DB(self.path)
        self.httpd = make_server(cfgval("host"), cfgval("port"),
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
        if time.time() - self.lasttick > 60 * 5:
            self.lasttick = time.time()
            print(('[%s] Caching...' % (datetime.now().strftime('%D %T'))))
            #Get a list of weapons from the last played game
            with self.db:
                lastgame = self.db.con.execute(
                    "SELECT id FROM games ORDER BY id DESC").fetchone()[0]
                cache.weaponlist = [r[0] for r in self.db.con.execute(
                    "SELECT weapon FROM game_weapons WHERE game = %d" % (
                        lastgame))]
            self.tcache = {
                "servers": {}
                }
            with self.db:
                self.tcache["servers"] = cache.servers(self.db)
                self.tcache["games"] = cache.games(self.db)
                self.tcache["players"] = cache.players(self.db,
                    recentlimit=cfgval("playerrecent"))
                self.tcache["weapons"] = cache.weapons(self.db,
                    recentlimit=cfgval("weaponrecent"))
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

        def simplereturn(q):
            if query:
                if query not in self.cache[q]:
                    return nferr
                return self.cache[q][query]
            return self.cache[q]
        with self.cachelock:
            if name in ["server", "servers"]:
                return simplereturn("servers")
            elif name in ["player", "players"]:
                return simplereturn("players")
            elif name in ["game", "games"]:
                return simplereturn("games")
            elif name in ["weapon", "weapons"]:
                return simplereturn("weapons")
            else:
                return inverr

server = Server()
while True:
    server.tick()
    time.sleep(1)