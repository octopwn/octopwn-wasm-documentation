<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Script

The `SCRIPT` block lets you drop a Python coroutine into the middle of a flowgraph for the cases where the existing filter / transform vocabulary is not enough. See the [script block guide](../script-block.md) for the `process(item, octopwn)` contract and a couple of worked examples.

---

**1 block type(s) in this category.**

---

### `SCRIPT`

*Category: `SCRIPT`*

User-scriptable Python block. Double-click to edit code.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `in` | input | `any` | no | Input items — one passed to process() at a time |
| `out` | output | `any` | no | Output items returned by process() |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `code` | `str` | `async def process(item, octopwn):
    """
    Process a single input item.

    Args:
        item:     One item from the 'in' port
        octopwn:  The OctoPwn application context

    Returns:
        A single item, a list of items, or None to drop.
    """
    # implement here
    return item
` | no | Python source code |
| `input_type` | `str` | `any` | no | Semantic type of input items |
| `output_type` | `str` | `any` | no | Semantic type of output items |

---
