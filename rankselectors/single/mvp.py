# -*- coding: utf-8 -*-
from rankselectors import single


class Selector(single.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Team Scores: Last %d days" % self.days
        self.tabletitle = ("Player", "Score")
        self.playerkey = lambda x: x['score']
        self.uniqueplayers = 4
        self.q[self.opts] = []
