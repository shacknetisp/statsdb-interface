# -*- coding: utf-8 -*-
import sqlite3
import shutil
from threading import Lock


class DB:

    def __init__(self, path):
        self.path = path
        self.lock = Lock()

    def __enter__(self):
        self.lock.acquire()
        self.con = sqlite3.connect(self.path)
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

    def backup(self, backupfile):
        self.lock.acquire()
        # Copy the DB
        self.con = sqlite3.connect(self.path)
        cur = self.con.cursor()
        cur.execute('BEGIN IMMEDIATE')
        shutil.copyfile(self.path, backupfile)
        self.con.rollback()
        self.con.close()
        self.lock.release()
