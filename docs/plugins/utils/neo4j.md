# Neo4j Utility

The **Neo4j** utility is a thin OctoPwn-side client for an **external Neo4j
instance** — typically the one backing a [BloodHound CE](https://github.com/SpecterOps/BloodHound)
deployment. It lets an analyst run arbitrary Cypher queries (or BloodHound
path queries) without leaving the OctoPwn session and without context-switching
to the BloodHound web UI for quick checks.

It is **not** a graph-store of its own. It does not import data, ingest
BloodHound zip files, or persist anything in OctoPwn — it is purely a query
front-end. The data must already be loaded into Neo4j by something else
(typically the BloodHound CE backend, populated by the [BLOODHOUND
utility](bloodhound.md) or the
[`SNAFFLER`](../scanners/snaffler.md)-collected zips).

---

## How it differs from the BloodHound utility

| Feature | `BLOODHOUND` util | `NEO4J` util |
| --- | --- | --- |
| Collects data from a live AD | yes | no |
| Produces BloodHound-compatible zip | yes | no |
| Sends data to a Neo4j instance | indirectly (via BH ingestor) | reads only |
| Runs Cypher queries | no | yes |
| Returns BloodHound-style paths | no | yes (`querypath`) |

Use **BLOODHOUND** to *create* the graph; use **NEO4J** to *query* it on the
fly from inside an OctoPwn session.

---

## Connectivity model

Because OctoPwn runs in the browser (WASM) or in a server context that does
not by default have arbitrary outbound access, Neo4j has to be reachable
**from the runtime that hosts OctoPwn**:

- **Pro / WASM build** — the Neo4j Bolt URL is reached by the WSNet proxy. It
  must therefore be reachable from the host running the WSNet daemon (often
  `localhost:7687` on the analyst's workstation when BloodHound CE is running
  next to OctoPwn).
- **Enterprise / server build** — Bolt URL must be reachable from the server.
  Same `localhost:7687` story when BloodHound CE is co-located.

There is no built-in proxy / pivot path for Bolt — if the Neo4j instance is
behind a firewall, expose it locally first.

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `url` | `bolt://localhost:7687` | Bolt URI. `bolt+s://...` works for TLS. |
| `username` | `neo4j` | Database user. |
| `password` | `mynewpassword` | Database password. |
| `threshold` | `5000` | Hard cap on rows returned per query. Queries that exceed this are aborted unless invoked with `force=True`. |

The defaults match the documented BloodHound CE quick-start install — change
them for any production setup.

---

## Commands

### GENERIC

#### connect
`connect(url, username, password, threshold)` — open the Bolt session and run
a `RETURN 1 AS ok` smoke test. If the smoke test fails (auth wrong, instance
down, wrong protocol) the session does **not** transition to connected and
the error is printed.

Any of the four arguments left empty falls back to the corresponding session
parameter, so a parameterised session can simply call `connect`.

#### disconnect
Close the Bolt session. Idempotent — calling on an already-disconnected util
returns `True`.

### QUERY

#### query
`query(query, force=False)` — run an arbitrary Cypher query. Result is
returned as a JSON-serialised list of records and printed in the session
window.

If the result set would exceed `threshold` rows, the query is **rejected**
to protect the browser from memory pressure. Pass `force=True` to bypass the
guard for queries you've already sized up.

Example:

```cypher
MATCH (u:User {enabled: true}) RETURN u.name, u.description
```

#### querypath
`querypath(query, force=False)` — run a Cypher query that returns **paths**
(`MATCH p = ...`). Results are post-processed into BloodHound-style step
arrays (node-edge-node-edge-...) suitable for the same downstream consumers
as the [DOMAIN utility](domain.md)'s `pathto*` commands.

Example:

```cypher
MATCH p = shortestPath((u:User {name: 'BOB@CONTOSO.LOCAL'})-[*1..10]->(:Group {name: 'DOMAIN ADMINS@CONTOSO.LOCAL'}))
RETURN p
```

`force` semantics are identical to `query`.

---

## Limitations and caveats

- **No write protection** — the util will happily run `DELETE` /
  `DETACH DELETE` queries. There is no read-only enforcement on the OctoPwn
  side; if you need that, configure a read-only Neo4j user.
- **No schema introspection** — there are no helpers to list labels,
  relationship types, or properties. Use the BloodHound web UI or the Neo4j
  browser for exploration; use this util to *execute* known queries.
- **Threshold is row count, not byte count.** A query returning 100 huge
  paths can still bog the session down — use `LIMIT` in the query itself.
- **Single connection per session.** Calling `connect` while already
  connected raises an error; `disconnect` first.

---

## See also

- [BLOODHOUND utility](bloodhound.md) — the *collection* side: turns an AD
  domain into a BloodHound zip ready for ingestion into BloodHound CE
  (which in turn populates the Neo4j you connect to here).
- [DOMAIN utility](domain.md) — uses the BloodHound graph (loaded from a zip,
  not from Neo4j) to compute paths and orchestrate end-to-end ACL-based
  attacks.
- [BloodHound CE](https://github.com/SpecterOps/BloodHound) — the upstream
  graphing project; install it locally and point this util at its Neo4j.
