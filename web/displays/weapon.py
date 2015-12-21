# -*- coding: utf-8 -*-
import dbselectors
import web
import utils
from redeclipse import redeclipse


def single(request, db, specific):
    ws = dbselectors.get('weapon', db, {'recentsums': ['-1']})
    weapons = ws.multi()
    weapon = ws.single(specific)
    if utils.sok(weapon):
        totalwielded = sum(w['timewielded'] for w in list(weapons.values()))
        ret = web.displays.weapontable(
            weapon,
            totalwielded).html(True)
    else:
        ret = "<div class='center'><h2>No such mutator.</h2></div>"
    return web.page(ret, title=specific.capitalize())


def multi(request, db):
    ws = dbselectors.get('weapon', db, {'recentsums': ['-1']})
    weapons = ws.multi()
    totalwielded = sum(w['timewielded'] for w in list(weapons.values()))
    ret = web.displays.weaponstable(
        weapons, totalwielded, redeclipse().weaponlist).html(True)
    return web.page(ret, title="Weapons")