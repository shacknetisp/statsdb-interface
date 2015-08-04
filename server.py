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
import dbselectors

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
        result = b""
        r = api.make(self.server,
            self.server.db, urllib.parse.parse_qs(
                    environ['QUERY_STRING'], True), environ['PATH_INFO'])
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
        self.path = homedir + '/stats.sqlite'
        self.db = db.DB(self.path)
        self.dblock = Lock()
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
            if select.select([self.httpd], [], [], 3)[0]:
                with self.dblock:
                    with self.db:
                        self.httpd.handle_request()

    def tick(self):
        if time.time() - self.lasttick > 60 * 1:
            self.lasttick = time.time()
            #Determine if the database exists
            with self.dblock:
                with self.db:
                    self.dbexists = self.db.con.execute(
                            "PRAGMA table_info(games)").fetchone(
                                ) is not None
                    if self.dbexists:
                        self.dbexists = self.db.con.execute(
                            "SELECT id FROM games ORDER BY id DESC").fetchone(
                                ) is not None
            if self.dbexists:
                #Get a list of weapons from the last played game
                with self.dblock:
                    with self.db:
                        lastgame = self.db.con.execute(
                        "SELECT id FROM games ORDER BY id DESC").fetchone()[0]
                        dbselectors.weaponlist = [
                        r[0] for r in self.db.con.execute(
                        "SELECT weapon FROM game_weapons WHERE game = %d" % (
                            lastgame))]
            #Create a backup, remove old backups
            with self.dblock:
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