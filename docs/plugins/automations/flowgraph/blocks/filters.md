<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Filters, gates and collectors

Filter blocks evaluate conditions on flowing items. `FILTER` and `FILTER_TARGETS` route items between `match` and `no_match` outputs based on a key / op / value triple. `COLLECT` accumulates items into a re-emittable store that feeds the `lookup` port of FILTER for set-membership checks. `GATE` is a flow-control toggle. `PAIR_DEDUP` cross-products targets × credentials and emits only `(tid, cid)` pairs not yet seen this runloop. `PORT_GATE` only lets targets through that have a given port open, running an automatic portscan if no port data exists yet.

---

**6 block type(s) in this category.**

---

### `FILTER`

*Category: `FILTER`*

Evaluates a single condition on each incoming dict-shaped item. Items that pass go to the "match" port; items that fail go to "no_match". For set-membership checks wire a COLLECT.store to the optional "lookup" port, set op=in or op=not_in, and set value to the field name to extract from each lookup item.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any dict-shaped item (scanner result, etc.) |
| `lookup` | input | `any` | yes | Optional lookup items for in/not_in ops — wire from COLLECT.store |
| `match` | output | `any` | no | Items where condition is true |
| `no_match` | output | `any` | no | Items where condition is false |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `key` | `str` |  | yes | Dict key to evaluate, e.g. "port" or "share" |
| `op` | `str` | `eq` | no | Operator: eq \| ne \| gt \| lt \| contains \| in \| not_in |
| `value` | `str` |  | yes | Value to compare against, or field name to extract from lookup items for in/not_in |

---

### `FILTER_TARGETS`

*Category: `FILTER`*

Filters target dicts from SOURCE_TARGETS or scanner outputs. op=contains on list fields checks substring membership — e.g. key=ports, op=contains, value=445 matches targets with 445/TCP open. Other useful keys: ip, hostname, isdc, ostype, samaccountname. For set-membership checks wire a COLLECT.store to the optional "lookup" port and use op=in or op=not_in.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `scan_result` | no | Target dict from SOURCE_TARGETS / SOURCE_TARGETS_NEW |
| `lookup` | input | `any` | yes | Optional lookup items for in/not_in ops — wire from COLLECT.store |
| `match` | output | `scan_result` | no | Targets where condition is true |
| `no_match` | output | `scan_result` | no | Targets where condition is false |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `key` | `str` |  | yes | Target field to evaluate, e.g. "ports", "ip", "isdc" |
| `op` | `str` | `eq` | no | Operator: eq \| ne \| gt \| lt \| contains \| in \| not_in |
| `value` | `str` |  | yes | Value to compare against, or field name to extract from lookup items for in/not_in |

---

### `COLLECT`

*Category: `FILTER`*

Collects all incoming items; re-emits them from the store output. Wire store → FILTER.lookup to enable in/not_in set-membership ops. Set dedup=true + key=<field> to emit only the first item per unique field value.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Items to collect |
| `store` | output | `any` | no | All collected (and optionally deduped) items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `name` | `str` | "" | no | Store name for cross-run persistence (optional) |
| `dedup` | `bool` | false | no | Remove duplicate items |
| `key` | `str` | "" | no | Field for dedup identity (empty = stringify item) |

---

### `GATE`

*Category: `FILTER`*

Flow-control gate: passes all data through when the trigger fires, blocks everything otherwise. Use default_open to invert behavior when the trigger port is not wired.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Items to pass through or block |
| `trigger` | input | `any` | yes | Gate opens when this port receives any item |
| `data` | output | `any` | no | Passed-through items (empty when gate is closed) |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `default_open` | `bool` | false | no | When true, data passes through if trigger is not wired. When false (default), data is blocked unless trigger fires. |

---

### `PAIR_DEDUP`

*Category: `FILTER`*

Cross-products credentials x targets and emits only (tid, cid) pairs not yet seen in previous runloop iterations. Wire into scanner or session pair ports to avoid re-scanning already-processed combos.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `scan_result` | no | Target items with __tid |
| `credential` | input | `credential` | no | Credential items with __cid |
| `pair` | output | `scan_result` | no | New (tid, cid) pair dicts |

**Parameters**

*No parameters.*

---

### `PORT_GATE`

*Category: `FILTER`*

Passes only targets that have a specific port open. Checks the target store first; if no port data exists, runs a portscan automatically. Targets without the port are emitted on the no_port output.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Targets to check |
| `target` | output | `scan_result` | no | Targets with the port confirmed open |
| `no_port` | output | `scan_result` | no | Targets where the port is closed or unreachable |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `port` | `int` | `445` | no | Port number to require |
| `protocol` | `str` | `TCP` | no | Protocol (TCP or UDP) |
| `timeout` | `int` | `5` | no | Portscan timeout per host (sec) |

---
