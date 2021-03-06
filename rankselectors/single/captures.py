# -*- coding: utf-8 -*-
from rankselectors import single


class Selector(single.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Player Captures: Last %d days" % self.days
        self.tabletitle = ("Player", "Captures")
        self.playerkey = lambda x: len(x['captures'])
        self.uniqueplayers = 4
        self.extraflags = ["affinities", "playeraffinities"]
