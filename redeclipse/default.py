# -*- coding: utf-8 -*-
import cgi
from collections import OrderedDict


class RE:

    def __init__(self):
        #Core mode names
        cmodestr = {}
        for k, v in list(self.modes.items()):
            cmodestr[v] = k

        #Create Mutator Lists
        gspnum = self.basemuts.index("gsp") - 1
        self.basemuts = self.tomuts(self.basemuts)
        del self.basemuts["gsp"]
        self.mutators.update(self.basemuts)
        for mode, modemuts in list(self.gspmuts.items()):
            modemuts = self.tomuts(modemuts, gspnum)
            self.gspmuts[mode] = modemuts
            self.mutators.update(modemuts)

    # Weapon Columns
    weapcols = ['timewielded', 'timeloadout']
    for a in ['damage',
        'hits', 'shots',
        'flakhits', 'flakshots',
        'frags']:
            weapcols += [a + '1', a + '2']

    #Misc Functions that have a slight possibility of changing
    def mutslist(self, game, html=False, short=False):
        muts = []

        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        for m in self.basemuts:
            if (game["mutators"] & self.basemuts[m]):
                muts.append(m)

        if game['mode'] in self.gspmuts:
            for m in self.gspmuts[game['mode']]:
                if (game["mutators"] & self.gspmuts[game['mode']][m]):
                    muts.append(m)
        if html:
            if short:
                out = []
                for m in muts:
                    out.append(m)
                return cgi.escape('-'.join(out))
            outl = chunks(muts, 3)
            htmll = []
            for chunk in outl:
                htmll.append(cgi.escape(" ".join(chunk)))
            return "<br>".join(htmll)
        return muts

    def tomuts(self, l, a=0):
        ret = OrderedDict()
        for i, mut in enumerate(l):
            ret[mut] = 1 << (i + a)
        return ret

    def scorestr(self, game, score):
        """Display score as a str, as time or points depending on the game."""
        import timeutils
        if (game["mode"] == self.modes["race"]
            and game["mutators"] & self.mutators["timed"]):
                if score == 0:
                    return '-'
                return timeutils.durstr(score / 1000, dec=True, full=True)
        return str(score)

    def modeimg(self, mode, c=24):
        return '''<img class="img%d"
        title="%s" src="%s" alt="%s">''' % (c, self.modestr[mode],
            "/images/modes/%d.png" % mode,
            self.modestr[mode])

    def weaponimg(self, weap, c=24):
        return '''<img class="img%d"
        title="%s" src="%s" alt="%s">''' % (c, weap,
            "/images/weapons/%s.png" % weap,
            weap)

    def teamimg(self, t, c=24):
        return '''<img class="img%d"
        title="%s" src="%s" alt="%s">''' % (c, t,
            "/images/teams/%s.png" % t,
            t)
