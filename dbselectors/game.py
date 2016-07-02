# -*- coding: utf-8 -*-
import dbselectors
from redeclipse import redeclipse


class Selector(dbselectors.Selector):

    def __init__(self, *args, **kwargs):
        self.flags = [
            "server",
            "teams", "affinities", "rounds",
            "players", "playerdamage", "playeraffinities", "playerweapons",
            "weapons"]
        super(Selector, self).__init__(*args, **kwargs)

    def fromrow(self, row):
        if not row:
            return {}
        ret = {
            "teams": {},
            "players": {},
            "weapons": {},
        }
        # Base
        dbselectors.rowtodict(ret, row, ["id", "time",
            "map", "mode", "mutators",
            "timeplayed"])
        ret["version"] = self.db.execute(
            """SELECT version FROM game_servers
            WHERE game = %d""" % ret['id']).fetchone()[0]
        # Server handle
        if self.flags["server"]:
            ret["server"] = self.db.execute(
                """SELECT handle FROM game_servers
                WHERE game = %d""" % ret['id']).fetchone()[0]
        # Teams
        if self.flags["teams"]:
            for team_row in self.db.execute(
                "SELECT * FROM game_teams WHERE game = %d" % row[0]):
                    team = {}
                    dbselectors.rowtodict(team, team_row,
                        [None, "team", "score", "name"])
                    ret["teams"][team["name"]] = team
        # Affinities
        captures = []
        bombings = []
        if self.flags["affinities"]:
            # Flag Captures
            for capture_row in self.db.execute(
                "SELECT * FROM game_captures WHERE game = %d" % row[0]):
                    capture = {}
                    dbselectors.rowtodict(capture, capture_row, [None,
                        "player", "playerhandle", "capturing", "captured"])
                    captures.append(capture)
            if captures:
                ret['captures'] = captures
            # Base Bombings
            for bombing_row in self.db.execute(
                "SELECT * FROM game_bombings WHERE game = %d" % row[0]):
                    bombing = {}
                    dbselectors.rowtodict(bombing, bombing_row, [None,
                        "player", "playerhandle", "bombing", "bombed"])
                    bombings.append(bombing)
            if bombings:
                ret['bombings'] = bombings
        # FFA Rounds
        if self.flags["rounds"]:
            ffarounds = []
            for ffaround_row in self.db.execute(
                "SELECT * FROM game_ffarounds WHERE game = %d" % row[0]):
                    ffaround = {}
                    dbselectors.rowtodict(ffaround, ffaround_row, [None,
                        "player", "playerhandle", "round", "winner"])
                    ffarounds.append(ffaround)
            if ffarounds:
                ret['ffarounds'] = ffarounds
        # Players
        if self.flags["players"]:
            for player_row in self.db.execute(
                "SELECT * FROM game_players WHERE game = %d" % row[0]):
                    player = {
                        "weapons": {},
                        "captures": [],
                        "bombings": [],
                        }
                    dbselectors.rowtodict(player, player_row, [None,
                        "name", "handle",
                        "score", "timealive", "frags", "deaths", "id",
                        "timeactive"])

                    #Player total damage
                    if self.flags["playerdamage"]:
                        player["damage"] = self.db.execute(
                                """SELECT (sum(damage1) + sum(damage2))
                                FROM game_weapons
                                WHERE game = %d AND player = %s""" % (
                                    row[0], player["id"])).fetchone()[0]

                    if self.flags["playeraffinities"]:
                        for capture in captures:
                            if capture["player"] == player["id"]:
                                player["captures"].append(capture)
                        for bombing in bombings:
                            if bombing["player"] == player["id"]:
                                player["bombings"].append(bombing)

                    if self.flags["playerweapons"]:
                        cols = ["weapon"] + redeclipse(ret).weapcols
                        for row in self.db.execute("""
                                    SELECT %s FROM game_weapons
                                    WHERE game = %d
                                    AND player = %d""" % (
                                        ','.join(cols), ret['id'], player_row[7]
                                        )):
                            weapon = row[0]
                            w = {'name': weapon}
                            for colidx in range(len(cols) - 1):
                                colidx += 1
                                t = cols[colidx]
                                try:
                                    w[t] = row[colidx]
                                except TypeError:
                                    w[t] = 0
                            player["weapons"][weapon] = w
                    ret["players"][player['id']] = player
        # Weapons
        if self.flags["weapons"]:
            for weapon in redeclipse(ret).weaponlist:
                w = {'name': weapon}
                gameweapsum = lambda x: self.db.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND game = %d""" % (
                        x, ret['id']),
                    (weapon,)).fetchone()[0]
                for t in redeclipse(ret).weapcols:
                    w[t] = gameweapsum(t)
                ret['weapons'][weapon] = w
        return ret

    def make_single(self, specific):
        row = self.db.execute("SELECT * FROM games WHERE id = ?",
            [specific]).fetchone()
        return self.fromrow(row) or {'error': 'Does not exist.'}

    def make_multi(self):
        f = self.makefilters(where=False)
        self.weakflags(['weapons', 'playerweapons', 'rounds'], False, True)
        ret = {}
        for row in self.db.execute(
            """SELECT * FROM games
            WHERE %s ORDER BY id DESC""" % (
                f[0] if f[0] else "1 = 1"), f[1]):
                    game = self.fromrow(row)
                    ret[game["id"]] = game
        return ret

    filters = [
        dbselectors.basicfilter("mode"),
        dbselectors.mathfilter("time"),
        dbselectors.mathfilter("timeplayed"),
        dbselectors.mathfilter("id"),
        dbselectors.mathfilter("uniqueplayers"),
        [{"key": "fighting", "sql": "mode != re_mode(id, 'race')"},
            {"key": "not-fighting", "sql": "mode == re_mode(id, 'race')"}],
        #Rank Keys
        [
            {"key": "affmvp", "sql": """mode != re_mode(id, 'race')
                AND (NOT (mutators & re_mut(id, 'survivor'))
                OR (mutators & re_mut(id, 'duel')))
                AND mode in (re_mode(id, 'ctf'), re_mode(id, 'bb'))"""},
            {"key": "dmmvp", "sql": """mode != re_mode(id, 'race')
                AND (NOT (mutators & re_mut(id, 'ffa'))
                OR (mutators & re_mut(id, 'duel'))
                OR (mutators & re_mut(id, 'survivor')))
                AND mode = re_mode(id, 'dm')"""},
            {"key": "ffa", "sql": """mode != re_mode(id, 'race')
                AND (mutators & re_mut(id, 'ffa'))"""},
            {"key": "ffasurv", "sql": """mode != re_mode(id, 'race')
                AND (mutators & re_mut(id, 'ffa'))
                AND (mutators & re_mut(id, 'survivor'))"""},
        ],
    ]
    xfilters = [
        dbselectors.basicxfilter("map"),
    ]

    def xfilter_players(self, v):
        handles = [p['handle'] for p in list(v["players"].values())]
        for handle in self.q["player"]:
            if handle not in handles:
                return False
        for handle in self.q["not-player"]:
            if handle in handles:
                return False
        return True
    xfilters.append(xfilter_players)

    def xfilter_mutators(self, v):
        if "mutator" in self.q:
            for mutator in self.qopt["mutator"]:
                try:
                    mutator = int(mutator)
                except:
                    return False
                if not (v["mutators"] & mutator):
                    return False
        for mutator in self.q["not-mutator"]:
            try:
                mutator = int(mutator)
            except:
                return False
            if v["mutators"] & mutator:
                return False
        return True
    xfilters.append(xfilter_mutators)
