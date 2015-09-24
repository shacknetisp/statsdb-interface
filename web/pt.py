# -*- coding: utf-8 -*-
import time
import dbselectors
import redeclipse
from .base import tdlink


def game(key, sel, days):
    ret = ""
    players = {}
    gs = dbselectors.GameSelector(sel)
    gs.gamefilter = """
    (%d - time) < (60 * 60 * 24 * %d)
    AND mode != %d""" % (time.time(), days, redeclipse.modes["race"])
    for game in list(gs.getdict().values()):
        for player in game["players"]:
            if player["handle"]:
                if player["handle"] not in players:
                    players[player["handle"]] = 0
                players[player["handle"]] += key(player)
    for player in sorted(list(players.items()), key=lambda x: -x[1])[:5]:
        ret += "<tr>"
        ret += tdlink("player", player[0], player[0])
        ret += "<td>%d</td>" % player[1]
        ret += "</tr>"
    return ret


def gamediv(key, akey, sel, days):
    ret = ""
    players = {}
    d = {}
    gs = dbselectors.GameSelector(sel)
    gs.gamefilter = """
    (%d - time) < (60 * 60 * 24 * %d)
    AND mode != %d""" % (time.time(), days, redeclipse.modes["race"])
    for game in list(gs.getdict().values()):
        for player in game["players"]:
            if player["handle"]:
                if player["handle"] not in players:
                    players[player["handle"]] = 0
                players[player["handle"]] += key(player)
                if player["handle"] not in d:
                    d[player["handle"]] = 0
                d[player["handle"]] += akey(player)
    for player in sorted(list(players.items()), key=lambda x: -x[1])[:5]:
        ret += "<tr>"
        ret += tdlink("player", player[0], player[0])
        ret += "<td>%d</td>" % round(player[1] / d[player[0]])
        ret += "</tr>"
    return ret


def mapnum(sel, days):
    ret = ""
    ms = {}
    gs = dbselectors.GameSelector(sel)
    gs.gamefilter = """
    (%d - time) < (60 * 60 * 24 * %d)""" % (time.time(), days)
    for game in list(gs.getdict().values()):
        if game["map"] not in ms:
            ms[game["map"]] = 0
        ms[game["map"]] += 1
    for m in sorted(ms, key=lambda x: -ms[x])[:5]:
        ret += "<tr>"
        ret += tdlink("map", m, m)
        ret += "<td>%d</td>" % (ms[m])
        ret += "</tr>"
    return ret


def servernum(sel, days):
    ret = ""
    ms = {}
    gs = dbselectors.GameSelector(sel)
    ss = dbselectors.ServerSelector(sel)
    gs.gamefilter = """
    (%d - time) < (60 * 60 * 24 * %d)""" % (time.time(), days)
    for game in list(gs.getdict().values()):
        if game["server"] not in ms:
            ms[game["server"]] = 0
        ms[game["server"]] += 1
    for m in sorted(ms, key=lambda x: -ms[x])[:5]:
        ret += "<tr>"
        ret += tdlink("server", m, ss.single(m)["desc"])
        ret += "<td>%d</td>" % (ms[m])
        ret += "</tr>"
    return ret