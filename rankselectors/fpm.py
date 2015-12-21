# -*- coding: utf-8 -*-
#Frags per Minute
from . import spx


class Selector(spx.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.playerkey = lambda x: x['frags']
        self.tabletitle = ("Player", "FPM")
        self.pagetitle = "Frags per Minute: Last %d days" % self.days
