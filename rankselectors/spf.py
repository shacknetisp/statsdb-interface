# -*- coding: utf-8 -*-
#Score per Frags
from . import spx


class Selector(spx.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.playerkey = lambda x: x['score']
        self.divby = lambda x: x['frags']
        self.rounddigits = 1
        self.tabletitle = ("Player", "S/F Ratio")
        self.pagetitle = "Score per Frags: Last %d days" % self.days
