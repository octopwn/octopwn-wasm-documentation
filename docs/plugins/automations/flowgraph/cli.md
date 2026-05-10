# CLI reference

The flowgraph framework is built around its UI, but every UI action is
ultimately implemented as a command on a `FLOWGRAPH` utility session.
That console is also exposed directly, which makes the CLI the right
tool for:

- **Scripted / unattended runs** — load a saved graph from disk and
  fire it from a CI pipeline or `clouderun.py`.
- **Replaying graphs** — re-execute the exact JSON you stored in the
  History tab for a previous engagement.
- **Validation in pre-commit** — run `validate` on the JSON before
  checking it in.
- **Headless investigations** — pull kill-chain reports for stored
  runs without opening the UI.

---

## Starting a session

From any OctoPwn console:

```
> createutil FLOWGRAPH
```

A FLOWGRAPH window opens in the frontend (if you are running with one)
and the console is now scoped to that session. From here, every
command in this page is available. The block registry is shipped to
the frontend automatically about a second after the window opens.

---

## Graph lifecycle

### `load <json_string>` / `loadfile <path>`

Parse and validate a flowgraph JSON. `load` accepts the JSON inline;
`loadfile` reads it from disk. Both broadcast the graph to the
frontend so the canvas updates immediately.

```
> loadfile /tmp/engagements/acme/wave1.json
[+] Flowgraph "wave1" loaded from file — 14 nodes, 21 edges
```

`load` is the right command when the JSON came from an upstream tool
(e.g. an LLM, a templating script). `loadfile` is what you will use
99% of the time.

### `validate [json_string]`

Validate the inline JSON, or — if omitted — the currently loaded
graph. Reports cycles, type mismatches, missing required params,
unreachable sinks and more. Returns the structured result as JSON so
CI pipelines can consume it.

```
> validate
[+] Flowgraph is valid.
[~] 1 warning(s).
  WARN   port-not-wired [node=tap-3]: Output port 'data' on TAP_SINK has no consumers.
```

### `listblocks`

Print every block type currently in the registry, grouped by category,
and re-broadcast the registry to the frontend. Useful when the palette
got out of sync.

### `listcomposites`

Print every registered composite (saved sub-flowgraph) with its port
surface and the directory it was loaded from. Composites live in
`~/.octopwn/composites/`.

### `savecomposite <path-to-json>` / `compositefromdata <json>` / `deletecomposite <id>`

Install or remove composite definitions. See
[composites](composites.md) for the workflow.

---

## Execution

### `run [start_at_iso] [stop_at_iso]`

Execute the loaded flowgraph once. RERUN_TRIGGER blocks cause
additional passes within the same `run` call. Optionally takes
ISO-8601 timestamps to schedule the start and force a stop:

```
> run                                                # start now
> run 2026-04-15T22:00:00                            # start at 22:00 today
> run 2026-04-15T22:00:00 2026-04-16T03:30:00        # ditto, hard stop at 03:30
```

The persistent `iter_state` carries across multiple `run` invocations
so `skip_done` flags work as expected. `resetstate` clears it.

### `continuous <interval_seconds> [start_at] [stop_at]`

Run the graph, sleep for `interval_seconds`, run it again, forever (or
until `stop_at` / `stop`). State is preserved across cycles.

```
> continuous 180                                     # every 3 minutes
> continuous 300 2026-04-15T22:00:00 2026-04-16T04:00:00
```

### `runloop [max_iterations]`

Iterate the graph until no new credentials or targets are discovered.
`max_iterations=0` (default) means unlimited.

```
> runloop 5
```

### `stop`

Cancel the running task and any scheduled stop timer.

### `status`

Print the current node states (PENDING / RUNNING / DONE / ERROR /
DISABLED) for the last engine run.

---

## Pacing and opsec

| Command                                  | Effect |
|------------------------------------------|--------|
| `setdelay <seconds>`                     | Seconds between RERUN_TRIGGER-driven passes (default 0). |
| `setmaxconcurrent <n>`                   | Cap simultaneous running nodes (0 = unlimited). |
| `setrate <ops_per_minute>`               | Cap node-start rate (0 = unlimited). |
| `setjitter <min_seconds> <max_seconds>`  | Random per-node startup delay range. |
| `setnodedelay <seconds>`                 | DEMO only — forces nodes to stay visible for at least N seconds. |
| `resetstate`                             | Clear `iter_state` (seen IDs, queues, journal). |

See [run modes & opsec](run-modes.md) for the bigger picture.

---

## Reporting

### `killchain <query_json> [hid]`

Walk the execution journal backwards from a stored item to reconstruct
the full kill-chain that produced it. `query_json` selects the item
(`{"__cid": 15}`, `{"__tid": 3}`, `{"__session_id": 7}`). The
optional `hid` selects a stored historical journal instead of the live
state.

```
> killchain {"__cid": 15}
> killchain {"__cid": 15} 7
```

See [reporting & killchain](reporting.md) for the journal format and
how to read the output.

---

## Typical scripted run

```
> createutil FLOWGRAPH
> setmaxconcurrent 4
> setrate 24
> setjitter 1 3
> setdelay 15
> loadfile /tmp/engagements/acme/wave1.json
> validate
[+] Flowgraph is valid.
> run 2026-04-15T22:00:00 2026-04-16T03:30:00
[+] Flowgraph "wave1" scheduled (start at 2026-04-15T22:00:00).
```

This is exactly what an unattended `clouderun.py` pentest would
execute, with the graph itself committed to git and traceable to the
operator who authored it.
