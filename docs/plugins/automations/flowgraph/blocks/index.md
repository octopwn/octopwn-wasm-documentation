<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Block reference

Complete, auto-generated reference for the **172** block types the flowgraph engine knows about. Regenerated from `octopwn/enterprise/flowgraph/registry.py` on every release — see the comment at the top of each page for the regeneration command.

For the high-level mental model, start with the [core concepts](../concepts.md) page; for examples that wire these blocks together end-to-end, see the [recipes](../recipes/index.md).

## Pages

### [Sources & prompts](sources.md) — 42 block(s)

Inject credentials, targets, sessions or interactive prompts into the pipeline.

*Covers categories: `SOURCE`, `PROMPT_SOURCE`.*

### [Queues, sinks, taps and console](queues-sinks.md) — 24 block(s)

Terminate pipelines, feed items back into the next runloop iteration, log items inline, or trigger another engine pass.

*Covers categories: `QUEUE`, `SINK`, `TAP`, `CONSOLE`.*

### [CredMux](credmux.md) — 1 block(s)

Routes a single credential stream onto protocol-typed output ports so each downstream block only sees credentials it can use.

*Covers categories: `CREDMUX`.*

### [Filters, gates and collectors](filters.md) — 6 block(s)

Conditional routing, flow gating, deduplication and port-gating of items as they move through the graph.

*Covers categories: `FILTER`.*

### [Scanners](scanners.md) — 49 block(s)

One block per entry in `OCTOPWN_SCANNER_TABLE` — all OctoPwn scanners exposed as flowgraph nodes.

*Covers categories: `SCANNER`.*

### [Sessions and ID splitters](sessions.md) — 17 block(s)

Open authenticated client sessions and unpack session / error items back into typed target + credential streams.

*Covers categories: `SESSION`.*

### [Session commands](commands.md) — 15 block(s)

Run any client command (LDAP, SMB, RDP, …) over a live session — the same surface as the interactive console.

*Covers categories: `COMMAND`.*

### [Attacks](attacks.md) — 8 block(s)

Curated, opinionated wrappers around the most common post-auth attacks (Kerberoast, DCSync, DPAPI, ADCS ESC1/4, …).

*Covers categories: `ATTACK`.*

### [Enumeration](enumeration.md) — 4 block(s)

Stream domain objects (users, computers, ADCS templates, trusts) from an open LDAP session.

*Covers categories: `ENUMERATION`.*

### [Transforms](transforms.md) — 3 block(s)

Convert credentials from one form to another — PKINIT U2U PFX → NT hash, hashcat wordlist / mask cracking.

*Covers categories: `TRANSFORM`.*

### [Script](script.md) — 1 block(s)

Drop a user-authored Python coroutine into the middle of a pipeline when the built-in vocabulary is not enough.

*Covers categories: `SCRIPT`.*

### [Composites and boundaries](composite.md) — 2 block(s)

Boundary blocks used to define the external port surface of reusable, named composite sub-flowgraphs.

*Covers categories: `BOUNDARY`.*
