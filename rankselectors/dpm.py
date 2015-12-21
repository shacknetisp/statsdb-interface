# -*- coding: utf-8 -*-
# Damage per Minute
from . import spx


class Selector(spx.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.playerkey = lambda x: x['damage']
        self.tabletitle = ("Player", "SPM")
        self.rounddigits = 0
        self.pagetitle = "Damage per Minute: Last %d days" % self.days
