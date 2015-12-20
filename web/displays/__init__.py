# -*- coding: utf-8 -*-
import importlib


#List of displays
#(<web calling points>, <display module>)
displays = [
    #(['', 'overview'], 'overview'),
    #(['game', 'games', 'g'], 'game'),
    (['server', 'servers', 's'], 'server'),
    #(['player', 'players', 'p'], 'player'),
    #(['weapon', 'weapons'], 'weapon'),
    (['map', 'maps'], 'map'),
    (['mode', 'modes'], 'mode'),
    #(['mut', 'mutator', 'muts', 'mutators'], 'mut'),
]


def importdisplay(s):
    c = importlib.import_module("web.displays." + s)
    return c

nd = {}
for d in displays:
    for an in d[0]:
        nd[an] = importdisplay(d[1])
displays = nd