# -*- coding: utf-8 -*-
import sqlite3
import os
import shutil
import time


class DB:

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.con = sqlite3.connect(self.path)
        self.con.row_factory = sqlite3.Row
        return self

    def __exit__(self, type, value, traceback):
        if type:
            self.con.rollback()
        else:
            self.con.commit()
        self.con.close()

    def backup(self, backupfile):
        self.con = sqlite3.connect(self.path)
        cur = self.con.cursor()
        cur.execute('BEGIN IMMEDIATE')
        shutil.copyfile(self.path, backupfile)
        self.con.rollback()
        self.con.close()


def flushdir(dir, maxage):
    now = time.time()
    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        if os.stat(fullpath).st_mtime < (now - maxage):
            if os.path.isfile(fullpath):
                os.remove(fullpath)