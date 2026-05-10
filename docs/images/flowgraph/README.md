# Flowgraph screenshot checklist

This folder holds every screenshot referenced by the flowgraph
documentation. The prose already includes the image links — they show
up as broken images until the screenshots below are captured and
dropped in with the exact filenames listed.

All screenshots should be taken against a live OctoPwn Enterprise
build at 100% zoom. Use a dark canvas background; the existing
documentation theme works against both, but the contrast is clearer in
dark mode.

When capturing:

- Crop tightly around the relevant UI; do not include taskbars,
  browser chrome or unrelated windows.
- PNG, max 1600 px wide. Re-export larger captures via `cwebp`,
  `pngquant` or similar before committing — the docs site has to
  load offline too.
- Where the shot mentions specific block ids, use those exact block
  ids so future readers can match the screenshot to the prose.

| Filename                       | Required content |
|--------------------------------|------------------|
| `01-util-create.png`           | The UTIL menu in the top bar with "Flowgraph" highlighted, or the moment after `createutil FLOWGRAPH` is typed. |
| `02-empty-canvas.png`          | Fresh FLOWGRAPH window: palette on the left, empty canvas in the centre, empty config panel on the right, toolbar visible at the top. |
| `03-palette-search.png`        | Palette search box with "scanner" typed; matching blocks (SCANNER_*) listed. |
| `04-drag-source.png`           | A `SOURCE_TARGETS` block dropped on the canvas; nothing else placed. |
| `05-wired-pipeline.png`        | Three-node pipeline `SOURCE_TARGETS → SCANNER_PORTSCAN → SCANNER_SMBFINGER` with the wires clearly visible. |
| `06-config-panel.png`          | The `SCANNER_PORTSCAN` node selected; right-hand config panel showing the `ports`, `timeout`, `skip_*` parameters. |
| `07-validation-error.png`      | The Validate popup with at least one error listed (for example: a SCANNER_SMBADMIN without a credential input wired). |
| `08-run-controls.png`          | Toolbar close-up showing the Run / Continuous / Runloop / Stop / Reset State buttons together with the pacing inputs (`maxconcurrent`, `rate`, `jitter`, `delay`). |
| `09-running-states.png`        | Mid-run snapshot: at least one PENDING (grey), one RUNNING (blue) and one DONE (green) node visible at the same time. |
| `10-tap-results.png`           | A `TAP_SINK` block selected on the canvas with the bottom / right results panel showing several inspected items in JSON. |
| `11-console-output.png`        | A `CONSOLE` block with its in-block log panel showing formatted log lines from real items (use a `message` template like `target={target} port={port}`). |
| `12-killchain.png`             | The kill-chain trace popup for a discovered credential, with multiple nested levels visible and at least one MITRE ATT&CK badge. |
| `13-save-composite.png`        | The Save Composite dialog open with a `COMPOSITE_<Something>` id and a description filled in; the inferred port surface visible. |
| `14-composite-reuse.png`       | A composite block dropped onto a fresh canvas, with its external input / output ports labelled and one or two of them wired up to other blocks. |

After capturing all 14 shots, run a `mkdocs serve` and click through
the UI tour + the recipes to make sure no `[broken image]` markers
remain. Then commit the PNGs together with this README in a single
"flowgraph: ship docs screenshots" commit.
