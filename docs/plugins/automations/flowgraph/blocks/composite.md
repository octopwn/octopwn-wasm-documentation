<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Composites and boundaries

Composite blocks let you turn a piece of a flowgraph into a reusable, named component with its own typed ports — think "save selection as block". The composite itself is an inner `Flowgraph` whose external interface is defined by the boundary nodes documented below. See the [composites guide](../composites.md) for the full authoring / saving / sharing workflow.

---

**2 block type(s) in this category.**

---

### `BOUNDARY_INPUT`

*Category: `BOUNDARY`*

Composite boundary: parent composite input is injected here as a source into the inner graph. Set external_port to the name of the composite input.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `out` | output | `any` | no | Data leaving the boundary into the inner graph |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `external_port` | `str` |  | yes | Name of the input port on the parent composite |
| `type_name` | `str` | `any` | no | Wire type for the parent port — controls connection compatibility |
| `output_port` | `str` | `out` | no | Inner output handle id (usually out) |

---

### `BOUNDARY_OUTPUT`

*Category: `BOUNDARY`*

Composite boundary: items wired here become outputs on the parent composite. Set external_port to the name of the composite output.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `in` | input | `any` | no | Data entering from the inner graph |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `external_port` | `str` |  | yes | Name of the output port on the parent composite |
| `type_name` | `str` | `any` | no | Wire type for the parent port |
| `input_port` | `str` | `in` | no | Inner input handle id (usually in) |

---
