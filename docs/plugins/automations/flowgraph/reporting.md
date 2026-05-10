# Reporting & killchain

Every flowgraph pass writes an **execution journal** to `iter_state`
and to the History database. The journal is what makes the killchain
report work: given any item in the store, OctoPwn can walk the journal
backwards and reconstruct the entire path that produced it.

This page explains what the journal contains, what `killchain`
produces, and how runs end up in the History tab.

---

## The execution journal

Every block invocation appends one entry to
`iter_state['execution_journal']`. Each entry is a dict that contains:

| Key                  | Meaning |
|----------------------|---------|
| `ts`                 | ISO-8601 timestamp of the invocation. |
| `event`              | `'pass_start'` for pass markers, otherwise the executor stamps this with the block category. |
| `node_id`            | The node id (UUID-shaped string) on the canvas. |
| `block_type`         | E.g. `SCANNER_SMBADMIN`, `CMD_DCSYNC`. |
| `params`             | The static params on the node (so the kill chain can show what `template=` you used). |
| `inputs`             | Per-input-port summaries — only the well-known ID keys (`__tid`, `__cid`, `__jid`, …) are kept, never the full item payload. |
| `outputs`            | Per-output-port summaries, same shape. |
| `iteration`          | Runloop pass number. |

The summaries are *intentionally* lightweight. The journal is meant to
be a provenance graph, not a results store — actual scan output goes
to the History DB and to `/browserfs/volatile`.

### Journal ID stamps (`__jid`)

When the engine appends a journal entry it assigns it a monotonically
increasing `__jid` integer and stamps every output item with that
same value. The next block to receive the item preserves `__jid` in
its input summary, which creates a direct parent link from the
consuming entry back to the producing one.

That is the *only* thing the killchain walker uses to traverse the
graph. No content matching, no heuristics — just `__jid` chains.

---

## `killchain` — what it actually does

`killchain <query_json> [hid]` finds the journal entry whose outputs
match the query (e.g. `{"__cid": 15}`), then walks parent links
backwards until it hits source blocks. The result is a tree of
`KillChainStep` objects rendered as both a human-readable text report
and a JSON tree (the latter is what the frontend uses to draw the
tree view).

A typical output looks like:

```
Kill chain for query {"__cid": 15}
  └── HASHCAT_WORDLIST [hashcat-1] (2026-04-15T22:04:11)
        params: { wordlist: rockyou.txt }
        T1110.002
        └── CMD_KERBEROAST [roast-1] (2026-04-15T22:03:55)
              T1558.003
              └── OPEN_SESSION_KERBEROS [opensess-1] (2026-04-15T22:03:48)
                    └── CREDMUX [mux-1] (2026-04-15T22:03:47)
                          └── SOURCE_CREDENTIALS_NEW [src-creds-1] (2026-04-15T22:03:46)
```

Read top to bottom: the cracked credential 15 came out of
`HASHCAT_WORDLIST`, which got its hash from `CMD_KERBEROAST`, which
ran over a Kerberos session opened with a different (existing)
credential routed through `CREDMUX`. The `T1110.002` / `T1558.003`
badges come from the `attack_techniques` field in the registry —
they map to MITRE ATT&CK and feed directly into a report appendix.

### Passthrough collapse

Blocks like `CMD_LDAP` re-emit the session reference on a
`session_out` port so chains can continue from them. The walker
detects passthrough entries (input has an item with the same ID keys
as the queried item) and collapses them, keeping the report focused on
the steps that actually transformed the data.

### Cross-run provenance

`SOURCE_*` blocks stamp items with `__source_flowgraph_hid` — the
history id of the run that originally introduced the item to the
store. When `killchain` walks a journal and finds an item with a
different `hid` than the current run, it loads the stored journal
for that historical run too and continues the trace there. The output
prints a `[*] Loaded historical journal for hid=N` line whenever this
happens.

That is how OctoPwn answers "where did this credential first come
from?" across an entire engagement, not just the latest run.

---

## History integration

Every `run`, `continuous` cycle and `runloop` allocates a fresh
history entry. The entry contains:

| Stored key       | Contents |
|------------------|----------|
| `__flowgraph`    | The full flowgraph JSON snapshot (so the History tab can re-render the exact graph that was run). |
| `__journal`      | The serialised execution journal (used by `killchain hid=…`). |
| `__run_meta`     | Run metadata: `flowgraph_name`, `passes`, `status` (`completed` / `stopped` / `error`), `mode` (`run` / `continuous` / `runloop`). |
| `__state_event`  | Per-node state transitions (so the timeline can replay PENDING → RUNNING → DONE). |
| `<node_id>::<port_name>` | Per-port data snapshots tagged with the iteration index. |

The History tab will:

- Show the run with its mode and final status.
- Let you re-open the saved graph on a fresh canvas (it loads via
  `FLOWGRAPH_LOADED_EXTERNAL`).
- Let you replay the per-port data inspector.
- Drive `killchain hid=<N>` against a historical run for after-action
  reports.

---

## Building a report from a run

For a clean engagement report:

1. Run the engagement graph with `setmaxconcurrent / setrate /
   setjitter` set as you would on the real network.
2. After it completes, open the History tab and note the `hid`.
3. For each "interesting outcome" (a new DA credential, a new
   sensitive share discovered, etc.), run
   `killchain {"__cid": <id>} <hid>` (or `{"__tid": <id>}`,
   `{"__session_id": <id>}`).
4. Paste the resulting tree directly into the engagement report — it
   is already ordered, timestamped and tagged with ATT&CK techniques.
5. The Vulnerability Reporting framework (Enterprise) consumes the
   same history entries to auto-build report sections from scanner
   results that produced findings.

The execution journal is small (item IDs, not item bodies), so even a
runloop that converged after 50 passes produces a journal that
serialises to a few hundred KB — small enough to ship with the report
as a verifiable audit trail.
