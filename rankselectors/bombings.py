# -*- coding: utf-8 -*-
from . import single


class Selector(single.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Player Bombings: Last %d days" % self.days
        self.tabletitle = ("Player", "Bombings")
        self.playerkey = lambda x: len(x['bombings'])
