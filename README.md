# portfree

Small stdlib-only helper for the three port questions that come up constantly
in local dev:

```python
from portfree import find, is_free, wait_open, who

find(8000)              # -> 8000 if free, else the next free port
is_free(5432)           # -> True/False
wait_open(5432, 10)     # block until something listens, up to 10s
who(5432)               # -> pid/process holding it, or None
```

## CLI

```
$ portfree 8000
8012

$ portfree --who 5432
postgres (pid 812)

$ portfree --wait 6379 --timeout 5
6379 open after 0.4s
```

## Why not just bind to port 0

Binding to `0` lets the OS pick, but you do not get to express a *preference*.
`find(8000)` means "8000 if you can, otherwise something near it" — which is
what you actually want when a dev server has a documented default port.

## Race condition warning

There is an unavoidable TOCTOU window: the port is free when checked and may be
taken by the time you bind. This module is for local development convenience,
not for allocation. If you need atomic allocation, bind with `SO_REUSEADDR`
and keep the socket.
