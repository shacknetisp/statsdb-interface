# -*- coding: utf-8 -*-
import dbselectors
from redeclipse import redeclipse
import utils
import cfg


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = [
            "games", "recentgames",
            "affinities",
            "recentsums", "damage", "weapons"]
        super(Selector, self).__init__(*args, **kwargs)

    def fromrow(self, row):
        if not row:
            return {}
        recentgames = self.q.qint('recentgames', cfg.get('recent'))
        recentsums = self.recent('recentsums')
        ret = {
            "recentgames": {},
            }
        dbselectors.rowtodict(ret, row, [
            "name", "handle"
            ], start=1)
        handle = ret['handle']
        # Games
        if self.flags['games']:
            gamerows = list(self.db.execute(
                """SELECT * FROM games
                WHERE id in (SELECT game FROM game_players
                WHERE handle=?)""", (handle,)))
            ret["games"] = [r[0] for r in gamerows]
            # Recent Games
            if self.flags['recentgames']:
                gs = dbselectors.get("game", self.db)
                gs.flags_none()
                for row in utils.sliceneg(
                    list(reversed(gamerows)), recentgames):
                    game = gs.fromrow(row)
                    # Count FFA rounds for this player in a new index
                    ffarounds = []
                    for ffaround_row in self.db.execute(
                        """SELECT * FROM game_ffarounds
                        WHERE playerhandle = ?
                        AND game = %d""" % game['id'], (handle,)):
                            ffaround = {}
                            dbselectors.rowtodict(
                                ffaround, ffaround_row, ["game",
                                None, None, "round", "winner"])
                            ffarounds.append(ffaround)
                    if ffarounds:
                        game['player_ffarounds'] = ffarounds
                    ret["recentgames"][game["id"]] = game

        #Data from games
        recentsum = lambda x: self.db.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_players
            WHERE game IN (SELECT id FROM games
            %s)
            AND %s
            AND handle = ?
            %s)""" % (x,
                "WHERE mode != re_mode(id, 'race')" if x not in
                ['timeactive'] else "",
                self.vlimit(),
                recentsums), (ret['handle'],)).fetchone()[0]
        recent = {
            'weapons': {},
            }

        # Affinity data
        if self.flags['affinities']:
            captures = []
            for capture_row in self.db.execute(
                """SELECT * FROM game_captures WHERE playerhandle = ?
                AND game in (SELECT id FROM games
                %s)""" % (recentsums), (handle,)):
                    capture = {}
                    dbselectors.rowtodict(capture, capture_row, ["game",
                        None, None, "capturing", "captured"])
                    captures.append(capture)
            if captures:
                ret['captures'] = captures
            bombings = []
            for bombing_row in self.db.execute(
                """SELECT * FROM game_bombings WHERE playerhandle = ?
                AND game in (SELECT id FROM games
                %s)""" % (recentsums), (handle,)):
                    bombing = {}
                    dbselectors.rowtodict(bombing, bombing_row, ["game",
                        None, None, "bombing", "bombed"])
                    bombings.append(bombing)
            if bombings:
                ret['bombings'] = bombings

        # Sums of data
        if self.flags['recentsums']:
            for t in ['frags', 'deaths', 'timealive', 'timeactive']:
                recent[t] = recentsum(t)

            # Damage
            if self.flags['damage']:
                recent["damage"] = self.db.execute(
                    """SELECT (sum(damage1) + sum(damage2)) FROM game_weapons
                        WHERE %s
                        AND playerhandle = ?
                        AND game IN (SELECT id FROM games
                        WHERE mode != re_mode(id, 'race'))
                        %s""" % (self.vlimit(),
                        recentsums),
                            (ret["handle"],)).fetchone()[0]

            if self.flags['weapons']:
                #Weapon Data
                for weapon in redeclipse().weaponlist:
                    wr = {'name': weapon}
                    recentsum = lambda x: self.db.execute(
                        """SELECT sum(%s) FROM
                        (SELECT * FROM game_weapons
                        WHERE weapon = ? AND playerhandle = ?
                        AND game IN (SELECT id FROM games
                        WHERE mode != re_mode(id, 'race'))
                        AND %s
                        %s)""" % (x,
                        self.vlimit(),
                        recentsums),
                        (weapon, ret['handle'])).fetchone()[0]
                    for t in redeclipse().weapcols:
                        wr[t] = recentsum(t)
                    recent['weapons'][weapon] = wr
        ret["recent"] = recent
        return ret

    def make_single(self, specific):
        row = self.db.execute(
            """SELECT * FROM game_players
            WHERE handle = ?
            ORDER BY ROWID DESC""", (specific,)).fetchone()
        return self.fromrow(row) or {'error': 'Does not exist.'}

    def make_multi(self):
        f = self.makefilters()
        handles = [r[0] for r in
        self.db.execute(
            """SELECT DISTINCT handle FROM game_players
            %s""" % f[0], f[1])]
        ret = {}
        self.weakflags(['recentgames', 'recentsums'], False)
        for handle in handles:
            if handle:
                ret[handle] = self.single(handle)
        return ret

    filters = [
        dbselectors.basicfilter("name", "GLOB"),
    ]
