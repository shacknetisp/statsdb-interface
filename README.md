# statsdb-interface
Web Server interface to a Red Eclipse statistics database.

Call with: `./server.py <path to master server home>`

Config is `statsserver.json` in the master server home directory, options in defaultconfig.json

Backups of the sqlite database will be created, one per day, and deleted after 30 days.

Web Points:

`<>` means a placeholder, `[]` means a LIKE placeholder.

* `/get`
 * `/servers[/handle]`
  * `?host=<IP>`
  * `?version=[version]`
