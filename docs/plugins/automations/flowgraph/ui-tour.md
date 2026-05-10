# UI tour

This page walks through the FLOWGRAPH window end-to-end: opening it,
the block palette, the canvas, the per-node configuration panel, the
run controls, the results inspector and the kill-chain viewer. Each
section is paired with a screenshot.

If you prefer learning by doing, jump to the
[Portscan + SMB finger recipe](recipes/portscan-smbfinger.md) — it
walks through assembling and running an actual flowgraph in seven
clicks.

---

## 1. Opening a FLOWGRAPH window

From the UTIL menu in the top bar, pick **Flowgraph**, or from any
console type `createutil FLOWGRAPH`. A new window opens with an empty
canvas; the block registry is pushed to the frontend automatically
about a second after the window mounts.

![Opening the Flowgraph window from the UTIL menu](/images/flowgraph/01-util-create.png "Create FLOWGRAPH util")

---

## 2. The empty canvas

The flowgraph window has three persistent panes:

- **Left** — the block palette (collapsible).
- **Centre** — the canvas where you wire blocks.
- **Right** — the configuration panel for the currently selected node
  (collapsible).

A toolbar across the top exposes the run controls (Run / Continuous /
Runloop / Stop / Reset State), a save / load button, validation,
zoom, and the composite save dialog.

![Empty canvas with palette docked on the left](/images/flowgraph/02-empty-canvas.png "Empty canvas")

---

## 3. The block palette

Blocks are grouped by category — the same categories the
[block reference](blocks/index.md) is organised around. Categories
expand and collapse; the search box at the top filters across every
block id and description.

A few tips:

- Search by **wire type** — typing `credential_smb` shows every block
  with an SMB-credential port.
- Search by **MITRE technique ID** — typing `T1558` shows every block
  that produces / consumes a Kerberos ticket attack.

![Palette filtered by the keyword "scanner"](/images/flowgraph/03-palette-search.png "Palette search")

---

## 4. Dropping a block on the canvas

Drag any block from the palette onto the canvas. The drop point is
exactly where you let go of the mouse; nodes can be repositioned
later with click-and-drag. A freshly dropped node has its default
parameter values applied and is marked `PENDING` until the next run.

![SOURCE_TARGETS dragged onto the canvas](/images/flowgraph/04-drag-source.png "Drag a source")

---

## 5. Wiring blocks together

Hover over a port — a small handle appears. Click and drag from an
output handle to an input handle. The editor highlights compatible
input ports in green and incompatible ones in red as you drag, so it
is hard to make a connection the engine will refuse.

![A small pipeline: SOURCE_TARGETS → SCANNER_PORTSCAN → SCANNER_SMBFINGER](/images/flowgraph/05-wired-pipeline.png "Wired pipeline")

---

## 6. The configuration panel

Click any node to open its configuration panel on the right. The
panel renders one input per parameter declared in the registry, with
the parameter description below it (this is the same text you can
read on the [block reference](blocks/index.md) page). Required
parameters are marked; defaults are pre-filled. Setting `description`
gives the node a memorable label on the canvas.

![Config panel for SCANNER_PORTSCAN showing parameters](/images/flowgraph/06-config-panel.png "Node config panel")

---

## 7. Validation

The Validate button runs the same logic as `validate` on the CLI.
Errors and warnings are listed in a popover; each entry has a
`node_id` / `edge_id` reference you can click to jump straight to the
offending node on the canvas. Common errors are missing required
parameters, dangling required input ports, and type mismatches you
somehow tricked the editor into accepting.

![Validation popup with a missing-input error highlighted](/images/flowgraph/07-validation-error.png "Validation popup")

---

## 8. Run controls

The toolbar exposes five execution controls plus the pacing knobs:

- **Run** — single pass with RERUN_TRIGGER convergence.
- **Continuous** — keep running on an interval.
- **Runloop** — iterate until the store stops growing.
- **Stop** — cancel the current run.
- **Reset state** — clear seen IDs, queues, and journal.

The pacing inputs (max concurrent, ops/min, jitter, rerun delay) live
in the same toolbar. See [run modes & opsec](run-modes.md) for what
each one does.

![Run / Continuous / Runloop / Stop / Reset State buttons in the toolbar](/images/flowgraph/08-run-controls.png "Run controls")

---

## 9. Live execution state

While a run is in flight, every node is coloured by its state:

| Colour     | Meaning                                                 |
|------------|---------------------------------------------------------|
| Grey       | `PENDING` — has not yet had all required inputs.        |
| Blue       | `RUNNING` — actively executing.                         |
| Green      | `DONE` — finished, produced output.                     |
| Red        | `ERROR` — raised an exception; details on hover.        |
| Hatched    | `DISABLED` — manually disabled by the operator.         |

The window also shows a per-node iteration counter when you are
inside a `runloop` or `continuous` run.

![Graph mid-run with PENDING / RUNNING / DONE colouring visible](/images/flowgraph/09-running-states.png "Live execution states")

---

## 10. Inspecting items on a wire — TAP_SINK

Drop a `TAP_SINK` block onto any wire (drag it on top, the editor
"splices" it into the connection). TAP forwards items downstream
unchanged, but every item it sees also appears in the results panel
under that node — full JSON, one row per item.

![TAP_SINK selected, results panel showing the items that flowed through it](/images/flowgraph/10-tap-results.png "TAP results")

---

## 11. The CONSOLE block

`CONSOLE` is a pass-through logger. Each item is rendered through the
`message` template (`{field_name}` placeholders interpolate fields
from the dict) and printed live in a panel inside the block itself.
Leave `message` empty to print raw JSON.

This is the right block when you want a "log line" view of a stream
without leaving the canvas.

![CONSOLE block showing live log output](/images/flowgraph/11-console-output.png "CONSOLE output")

---

## 12. Kill chain trace

Right-click any item in the results panel — or any credential / target
in the project store — and pick **Trace kill chain**. The frontend
sends a `killchain {"__cid": …}` command to the backend; the response
is rendered as an interactive tree showing every block that
contributed to the item, with MITRE ATT&CK badges where the registry
maps them.

![Kill chain trace popup for a discovered credential](/images/flowgraph/12-killchain.png "Kill chain trace")

---

## 13. Saving a composite

With one or more nodes selected, picking **Save as composite** in
the toolbar opens a dialog. You give the composite an ID
(`COMPOSITE_<MyName>`, validated by the same regex the CLI enforces),
a description, and confirm the inferred port surface (one port per
`BOUNDARY_INPUT` / `BOUNDARY_OUTPUT` in the selection).

After saving, the composite is in the palette under **Composites** and
in `~/.octopwn/composites/<id>.json` for sharing.

![Save composite dialog](/images/flowgraph/13-save-composite.png "Save composite dialog")

---

## 14. Reusing a composite

Composites behave exactly like any other block — they appear in the
palette with their ports and description, and they execute as a
nested engine inside the parent. Double-clicking a composite opens its
inner graph in a new tab so you can edit it; saving the inner graph
updates the composite definition everywhere.

![A composite dropped into a new pipeline showing its external port surface](/images/flowgraph/14-composite-reuse.png "Composite reuse")

---

## What's next

- For wire-type rules, see [typing & wiring](typing-and-wiring.md).
- For the run / continuous / runloop modes in detail, see
  [run modes & opsec](run-modes.md).
- For end-to-end pipelines you can copy and adapt, see the
  [recipes](recipes/index.md).
- For the complete catalogue of every block type, see the
  [block reference](blocks/index.md).
