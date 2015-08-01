# statsdb-interface
Web Server interface to a Red Eclipse statistics database.

Call with: `./server.py <path to master server home>`

Example config (statsserver.json):

```
{
    "host": '',
    "port": 28700
}
```

Backups of the sqlite database will be created, one per day, and deleted after 30 days.
