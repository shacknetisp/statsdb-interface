#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import db
import select
from wsgiref.simple_server import make_server, WSGIRequestHandler
from threading import Thread
import time
import os
import cfg
import api


class httpd:

    def __init__(self, server):
        self.server = server

    def __call__(self, environ, start_response):
        status = "500 Server Error"
        headers = {}
        result = b""

        # Handle the request
        with self.server.db:
            response = api.handle(api.Request(environ), self.server.db.con)
        # Output the response
        status = response.status
        headers = response.headers
        result = response.body
        start_response(status, list(headers.items()))
        return [result]


class httphandler (WSGIRequestHandler):

    # We'll do our own logging of requests
    def log_message(self, format, *args):
        pass


def flushdir(dir, maxage):
    now = time.time()
    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        if os.stat(fullpath).st_mtime < (now - maxage):
            if os.path.isfile(fullpath):
                os.remove(fullpath)


class Server:

    def __init__(self):
        self.lasttick = 0
        self.path = '%s/%s' % (cfg.home, cfg.get("sqlitedb"))
        self.httpd = make_server(cfg.get("host"), cfg.get("port"),
            httpd(self),
            handler_class=httphandler)
        self.db = db.DB(self.path)
        self.tick()
        # Start the Daemon Thread
        thread = Thread(target=Server.do_http, args=(self, ))
        thread.setDaemon(True)
        thread.start()
        print("Server running.")

    def do_http(self):
        while True:
            if select.select([self.httpd], [], [], 1)[0]:
                self.httpd.handle_request()

    def tick(self):
        if time.time() - self.lasttick >= 60 * 1:
            self.lasttick = time.time()
            #Create a backup
            backupfile = (cfg.home +
            "/statsdbbackups/" +
            time.strftime("%Y%m%d") + '.bak')
            if not os.path.exists(backupfile):
                self.db.backup(backupfile)
                print("Creating backup.")
            #Clear old backups
            flushdir(cfg.home + "/statsdbbackups",
                60 * 60 * 24 * cfg.get("backupkeepdays"))

server = Server()
while True:
    server.tick()
    time.sleep(1)