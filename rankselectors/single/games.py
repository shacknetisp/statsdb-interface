# -*- coding: utf-8 -*-
from rankselectors import single


class Selector(single.Selector):

    def __init__(self, *args, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self.pagetitle = "Player Games: Last %d days" % self.days
        self.tabletitle = ("Player", "Games")
        self.playerkey = lambda x: 1
