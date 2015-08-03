# statsdb-interface
Web Server interface to a Red Eclipse statistics database.

Call with: `./server.py <path to master server home>`

Config is `statsserver.json` in the master server home directory, options in defaultconfig.json

Backups of the sqlite database will be created, one per day, and deleted after 30 days.

## API Points:

`<>` means a placeholder, `[]` means a LIKE placeholder, `{}` is an optional set.

### `/get`
* `/servers{/handle}`
 * `?{not-}host=<IP>`
 * `?{not-}version=[version]`
 * `?{not-}flags=[flags]`
* `/game{/gameid}`
 * `?{not-}mode=<mode>`
 * `?{lt/gt/not-}timeplayed=<timeplayed>`
 * `?{lt/gt/not-}time=<time>`
 * (*List*) `?{not-}map=<map>`
 * (*List*) `?{not-}mutator=<mutator>`
 * (*List*) `?{not-}playerhandle=<playerhandle>`
