# The SCRIPT block

`SCRIPT` is the escape hatch. When `FILTER`, `COLLECT`, `CREDMUX` and
the other built-in vocabulary can't express what you need, drop a
`SCRIPT` block into the pipeline and write the logic in Python.

```mermaid
flowchart LR
    upstream[Upstream block] -->|in any| script[SCRIPT]
    script -->|out any| downstream[Downstream block]
```

The block is intentionally minimal: it has one input port `in` and one
output port `out`, both of wire type `any`. The shape of the data is
entirely up to you and the upstream / downstream blocks.

---

## The `process` contract

Every script must define a single top-level coroutine called `process`
with this signature:

```python
async def process(item, octopwn):
    """
    Process a single input item.

    Args:
        item:     One item from the 'in' port (any shape).
        octopwn:  The OctoPwn application context (octopwnobj).

    Returns:
        - A single item (forwarded on 'out'),
        - A list of items (each forwarded on 'out'),
        - or None (item is dropped).
    """
    return item
```

The default code you get when you place a fresh `SCRIPT` block is
exactly the template above. Double-click the block in the canvas to
edit; the code is stored in the node's `params['code']` field and
re-compiled at the start of each run.

A few behavioural details to internalise:

- **One call per item.** The engine pulls items from the `in` queue
  and awaits `process(item, octopwn)` for each one. There is no
  batch / fan-in mode; if you need that, use `COLLECT` upstream.
- **Lists are flattened.** Returning a list lets a single input
  produce multiple outputs. Returning `None` drops the item silently.
- **Exceptions abort the node.** Any unhandled exception inside
  `process` is wrapped into a `RuntimeError` with the original
  traceback and marks the node `ERROR` in the UI.

---

## Configuring the block

`SCRIPT` exposes three parameters in the config panel:

| Parameter      | Purpose |
|----------------|---------|
| `code`         | The Python source. Use the in-canvas editor — the IDE-style autocomplete works against `octopwnobj`. |
| `input_type`   | Semantic wire type advertised on the `in` port. Default `any`. Set to the actual upstream type if you want the editor to refuse incompatible connections. |
| `output_type`  | Semantic wire type advertised on the `out` port. Default `any`. Set this when you know exactly what your script produces — downstream FILTERs will then accept the connection. |

Setting `input_type` / `output_type` is optional but recommended for
scripts that live in shared composites — it makes the contract
explicit and lets the editor enforce it.

---

## Example 1 — Filter to a specific share name

The built-in `FILTER` block evaluates a single key/op/value. When you
need a richer condition, drop into a SCRIPT block:

```python
async def process(item, octopwn):
    """
    Keep SMB share results whose UNC ends with one of a handful of
    well-known sensitive share names.
    """
    interesting = {'sysvol', 'netlogon', 'replication', 'admin$', 'c$'}

    path = (item.get('path') or '').lower()
    name = path.rstrip('\\').rsplit('\\', 1)[-1]
    if name in interesting:
        return item
    return None
```

Set `input_type=scan_result` and `output_type=scan_result` so the
downstream consumer's FILTER autocompletes against the SMB share schema.

---

## Example 2 — Enrich credentials with a custom tag

Add a `__custom_tag` field every downstream block can branch on:

```python
async def process(item, octopwn):
    """Tag credentials with the source they came from for later reporting."""
    enriched = dict(item)
    enriched['__custom_tag'] = 'auto-dcsync-{}'.format(item.get('__cid', '?'))
    return enriched
```

Make sure to copy the original dict before mutating — items can flow
through multiple paths in parallel and mutating in place leads to
spooky-action-at-a-distance bugs.

---

## What you have access to

The `octopwn` argument is the live `octopwnobj` — the same object every
other block uses. From inside a script you can:

- Read / write the credential store via `octopwn.credentialMgr`.
- Read / write the target store via `octopwn.targetMgr`.
- Query open sessions via `octopwn.sessionMgr`.
- Trigger any of the helpers that the regular client / scanner /
  attack code uses internally.

That makes the SCRIPT block effectively unlimited in power and, by the
same token, **unsandboxed**. The same trust model as the OctoPwn IDE
window applies — if you didn't write the script, read it before you
run it.

---

## When to *not* use a script

If your script ends up being more than ~30 lines and looks like it
might be useful elsewhere, the right tool is usually a
[plugin](../../utils/pluginloader.md), not a script block. Plugins live
in `~/.octopwn/plugins/`, get autoloaded by `PLUGINLOADER`, can ship
their own UI, and are far easier to share with the team.

`SCRIPT` is for the cases where the logic is so specific to one
flowgraph that turning it into a plugin would just create paperwork.
