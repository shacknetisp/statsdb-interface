# -*- coding: utf-8 -*-
weaponlist = []


def dictfromrow(d, r, l, start=0):
    for i in range(len(l)):
        if l[i] is not None:
            d[l[i]] = r[i + start]


def players(db, recentlimit):
    pc = {}
    for row in db.con.execute(
        "SELECT DISTINCT handle FROM game_players"):
            player = {
                'handle': row[0]
                }
            lastrow = db.con.execute(
                """SELECT * FROM game_players
                WHERE handle = ?
                ORDER BY ROWID DESC""", (row[0],)).fetchone()
            dictfromrow(player, lastrow, [
                "name"
                ], start=1)
            player["games"] = [r[0] for r in
            db.con.execute(
                """SELECT game FROM game_players
                WHERE handle = ?""", (row[0],))]
            #Data from games
            recentsum = lambda x: db.con.execute(
                """SELECT sum(%s) FROM
                (SELECT * FROM game_players
                ORDER by ROWID DESC LIMIT %d)""" % (x, recentlimit)
                ).fetchone()[0]
            allsum = lambda x: db.con.execute(
                """SELECT sum(%s) FROM game_players""" % (x)
                ).fetchone()[0]
            alltime = {
                'weapons': {},
                }
            recent = {
                'weapons': {},
                }
            for t in ['frags', 'deaths']:
                recent[t] = recentsum(t)
                alltime[t] = allsum(t)
            #Weapon Data
            ##Individual Weapons
            for weapon in weaponlist:
                wr = {}
                wa = {}
                recentsum = lambda x: db.con.execute(
                    """SELECT sum(%s) FROM
                    (SELECT * FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?
                    ORDER by ROWID DESC LIMIT %d)""" % (x, recentlimit),
                    (weapon, player['handle'])).fetchone()[0]
                allsum = lambda x: db.con.execute(
                    """SELECT sum(%s) FROM game_weapons
                    WHERE weapon = ? AND playerhandle = ?""" % (
                        x),
                    (weapon, player['handle'])).fetchone()[0]
                for t in weapcols:
                    wr[t] = recentsum(t)
                    wa[t] = allsum(t)
                alltime['weapons'][weapon] = wa
                recent['weapons'][weapon] = wr
            player["alltime"] = alltime
            player["recent"] = recent
            pc[row[0]] = player
    return pc


def servers(db):
    sc = {}
    for row in db.con.execute(
        "SELECT DISTINCT handle FROM game_servers"):
            server = {
                "handle": row[0],
                }
            lastrow = db.con.execute(
                """SELECT * FROM game_servers
                WHERE handle = ?
                ORDER BY ROWID DESC""", (row[0],)).fetchone()
            dictfromrow(server, lastrow, [
                "flags", "desc", "version", "host", "port"
                ], start=2)
            server["games"] = [r[0] for r in
            db.con.execute(
                """SELECT game FROM game_servers
                WHERE handle = ?""", (row[0],))]
            sc[row[0]] = server
    return sc


def games(db):
    ret = {}
    for row in db.con.execute("SELECT * FROM games"):
        game = {
            "teams": {},
            "players": [],
            "weapons": {},
            }
        dictfromrow(game, row, ["id", "time",
            "map", "mode", "mutators",
            "timeplayed"])
        for team_row in db.con.execute(
            "SELECT * FROM game_teams WHERE game = %d" % row[0]):
                team = {}
                dictfromrow(team, team_row, [None, "team", "score", "name"])
                game["teams"][team["name"]] = team
        for player_row in db.con.execute(
            "SELECT * FROM game_players WHERE game = %d" % row[0]):
                player = {
                    "weapons": {},
                    }
                dictfromrow(player, player_row, [None,
                    "name", "handle",
                    "score", "timealive", "frags", "deaths"])
                for weapon in weaponlist:
                    w = {}
                    for t in weapcols:
                        w[t] = db.con.execute("""
                        SELECT %s FROM game_weapons
                        WHERE game = %d AND player = %d AND weapon = ?""" % (
                            t, game['id'], player_row[7]
                            ), (weapon,)).fetchone()[0]
                    player["weapons"][weapon] = w
                game["players"].append(player)
        for weapon in weaponlist:
            w = {}
            gameweapsum = lambda x: db.con.execute(
                """SELECT sum(%s) FROM game_weapons
                WHERE weapon = ? AND game = %d""" % (
                    x, game['id']),
                (weapon,)).fetchone()[0]
            for t in weapcols:
                w[t] = gameweapsum(t)
            game['weapons'][weapon] = w
        ret[row[0]] = game
    return ret


def weapons(db, recentlimit):
    ret = {}
    for weapon in weaponlist:
        wr = {}
        wa = {}
        recentsum = lambda x: db.con.execute(
            """SELECT sum(%s) FROM
            (SELECT * FROM game_weapons WHERE weapon = ?
            ORDER by ROWID DESC LIMIT %d)""" % (x, recentlimit),
            (weapon,)).fetchone()[0]
        allsum = lambda x: db.con.execute(
            """SELECT sum(%s) FROM game_weapons WHERE weapon = ?""" % (
                x),
            (weapon,)).fetchone()[0]
        for t in weapcols:
            wr[t] = recentsum(t)
            wa[t] = allsum(t)
        ret[weapon] = {
            'recent': wr,
            'alltime': wa,
            }
    return ret