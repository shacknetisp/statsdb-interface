# -*- coding: utf-8 -*-
#Score per Minute
from . import spx


class Selector(spx.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.playerkey = lambda x: x['score']
        self.tabletitle = ("Player", "SPM")
        self.pagetitle = "Score per Minute: Last %d days" % self.days
