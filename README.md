# Statistics Web Interface for [Red Eclipse](http://redeclipse.net)
Run with: `./server.py <path to master server home>`

# API
`/api/<selector>/<[optional specific request]>?<[optional flags and filters]>`

Flags:
* all-flags: Enable everything, overwritten by `flags` and `no-flags`
* clear-flags: Disable everything, overwritten by `flags` and `no-flags`
* flags: Enable a specific flag (`?flags=flag1&flags=flag2`)
* no-flags: Disable a specific flag like `flags`

Filters:

* Basic: Will only return entries if they match. (<filter>, not-<filter>)
* Math: Simple comparisions. (<filter>, not-<filter>, lt-<filter>, gt-<filter>)
* Basic OR: Will only return entries if they have one of the matches.
* Basic AND: Will only return entries with all of the matches.
* Basic GLOB: Will match SQLite GLOBs.

Limits: If < 0 return all, else limit number of games used to calculate.

## /api/games
* Flags: server, teams, affinities, rounds, players, playerdamage, playeraffinities, playerweapons, weapons
* Filters: mode (basic), time (math), timeplayed (math), id (math), map (basic OR), players (basic AND), mutators (basic AND)

## /api/maps
* Flags: recentgames, race
* Limits: recentgames

## /api/modes
* Flags: recentgames
* Limits: recentgames

## /api/muts
* Flags: recentgames
* Limits: recentgames

## /api/players
* Flags: games, recentgames, affinities, recentsums, damage, weapons
* Filters: name (basic GLOB)
* Limits: recentgames, recentsums

## /api/servers
* Flags: games, recentgames
* Filters: host (basic), version (basic GLOB), authflags (basic GLOB)
* Limits: recentgames

## /api/weapons
--
