# -*- coding: utf-8 -*-
import sqlite3
import shutil
from threading import Lock
import redeclipse


class DB:

    def __init__(self, path):
        self.path = path
        self.lock = Lock()

    def __enter__(self):
        self.lock.acquire()
        self.con = sqlite3.connect(self.path)
        for f in redeclipse.functions:
            self.con.create_function(f.name, f.numparams, f(self))
        self.con.row_factory = sqlite3.Row
        return self

    def __exit__(self, type, value, traceback):
        # Rollback on an exception, commit if there's no error.
        if type:
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()
        self.lock.release()

    def execute(self, *args):
        return self.con.execute(*args)

    def backup(self, backupfile):
        with self.lock:
            # Copy the DB
            self.con = sqlite3.connect(self.path)
            cur = self.con.cursor()
            cur.execute('BEGIN IMMEDIATE')
            shutil.copyfile(self.path, backupfile)
            self.con.rollback()
            self.con.close()
