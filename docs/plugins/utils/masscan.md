# Masscan Utility

!!! warning "Deprecated"
    The standalone Masscan utility is **deprecated**. Use the Masscan importer
    in the [Targets window](../../user-guide/target.md) instead — it supports
    the same XML format, plus the GUI gives you per-target review before
    committing to the project's target list.

The legacy utility parses a [Masscan](https://github.com/robertdavidgraham/masscan)
XML output file and can populate the [Targets
window](../../user-guide/target.md) with the discovered hosts (with
their open ports attached). It does not perform any scanning itself —
Masscan must be run separately and its XML transferred into OctoPwn's
working directory first.

---

## Commands

### GENERIC

#### load
`load(filepath)` — load a Masscan XML file. The path must be reachable from
the OctoPwn runtime (i.e. inside the browser virtual filesystem on the WASM
build, or a real path on the server build).

#### addtargets
`addtargets()` — for every host in the loaded scan, register a [Target]
(../../user-guide/target.md) with the discovered open ports attached.
Hostname is left blank (Masscan output does not contain hostnames). The
target's `source` field is set to `MASSCAN:<filepath>` so the origin is
traceable in the Hub.

---

## See also

- [NMAP utility](nmap.md) — same idea but for richer Nmap XML output (with
  service / version detection and service-aware listings).
- [Targets window](../../user-guide/target.md) — the recommended way to
  import Masscan results going forward.
