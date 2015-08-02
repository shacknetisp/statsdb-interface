# statsdb-interface
Web Server interface to a Red Eclipse statistics database.

Call with: `./server.py <path to master server home>`

Config is `statsserver.json` in the master server home directory, options in defaultconfig.json

Backups of the sqlite database will be created, one per day, and deleted after 30 days.

The web server has minimal wait time, it runs from a cache that is updated by a seperate thread.

Web Points:

* /get
 * ?name={server,servers}&id=[handle]
 * ?name={player,players}&id=[handle]
